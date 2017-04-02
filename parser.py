from units import PhraseMatrix
from documentprocessor import DocumentProcessor

class Parser():
	DEFAULT_MAXIMUM_SENTENCE = 10;
	DEFAULT_ALTERNATIVE_VP_THRESHOLD = 0.75;
	DEFAULT_MAX_WORD_LENGTH = 100;
	MIN_SENTENCE_LENGTH = 5;
	MINIMUM_VERB_LENGTH = 2;

	def __init__(self, max_sentence, alternative_vp_threshold, max_word_length, is_TAC, threads=1):
		self.max_sentence = max_sentence
		self.alternative_vp_threshold = alternative_vp_threshold
		self.max_word_length = max_word_length
		self.threads = threads

		self.indicator_matrix = PhraseMatrix()
		self.compatibility_matrix = PhraseMatrix()
		self.alternative_VPs = PhraseMatrix()
		self.alternative_NPs = PhraseMatrix()

		self.noun_phrases = []
		self.verb_phrases = []
		self.all_phrases = []
		self.corefs = {}

		self.nouns = set()
		self.verbs = set()

		self.docs = []

		self.processor = DocumentProcessor()

	def build_compatibility_matrix(self):
		for np in self.noun_phrases:
			for vp in self.verb_phrases:
				related = self.check_relation(np, vp, self.noun_phrases, self.alternative_NPs)
				
				if not related:
					related = self.check_relation(vp, np, self.verb_phrases, self.alternative_VPs)

				if not related and (np, vp) in self.indicator_matrix
					related = True

				self.compatibility_matrix[(np, vp)] = int(related)

	def check_relation(phrase1, phrase2, other_phrase1s, alt_phrase1s):
		for other_phrase1 in other_phrase1s:
			if (phrase1, other_phrase1) in alt_phrase1s \
			and (other_phrase1, phrase2) in self.indicator_matrix:
				return True
		return False

	def calculate_jaccard_index(self, phrase1, phrase2):
		concepts_phrase1 = phrase1.concepts
		concepts_phrase2 = phrase2.concepts

		count = 0
		for concept in concepts_phrase1:
			if concepts_phrase2.find(concept):
				count += 1

		divisor = len(concepts_phrase1) + len(concepts_phrase2) - count
		
		if divisor == 0:
			return 0.0
		else:
			return float(count) / divisor

	def score_phrases(self):
		for doc in self.docs:
			scorer = PhraseScorer(doc)
			for phrase in self.all_phrases:
				score = scorer.score_phrases(phrase)
				phrase.score += score

	def find_alt_NPs(self, noun_phrases, clusters):
		for cluster in clusters:
			alt_phrases = []

			for phrase_text in cluster:
				for phrase in noun_phrases:
					if phrase.content == phrase_text:
						alt_phrases.append(phrase)

			len_alt_phrases = len(alt_phrases)
			for i in range(0, len_alt_phrases - 1):
				for j in range(0, len_alt_phrases):
					phrase1 = alt_phrases[i]
					phrase2 = alt_phrases[j]
					self.alternative_NPs[(phrase1, phrase2)] = 1
					self.alternative_NPs[(phrase2, phrase1)] = 1

	def find_alt_VPs(self, verb_phrases):
		len_verb_phrases = len(verb_phrases)
		for i in range(0, len_alt_phrases - 1):
			for j in range(0, len_alt_phrases):
				phrase1 = verb_phrases[i]
				phrase2 = verb_phrases[j]

				d = calculate_jaccard_index(phrase1, phrase2)
				if d >= self.alternative_vp_threshold:
					self.alternative_VPs[(phrase1, phrase2)] = d
					self.alternative_VPs[(phrase2, phrase1)] = d

	def find_optimal_solution(self):
		self.find_alt_VPs(self.noun_phrases, self.corefs.values())
		self.find_alt_VPs(self.verb_phrases)
		self.build_compatibility_matrix()
		return self.start_optimization()