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

	