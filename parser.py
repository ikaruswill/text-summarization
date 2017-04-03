from units import PhraseMatrix
from documentprocessor import DocumentProcessor
import gurobipy as g
import sys

class Parser():
	MIN_SENTENCE_LENGTH = 5
	MINIMUM_VERB_LENGTH = 2

	def __init__(self, max_sentence, alternative_vp_threshold, max_word_length, is_tac, threads):
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

		self.noun_variables = {}
		self.verb_variables = {}
		self.gamma_variables = {}
		self.noun_to_noun_variables = {}
		self.verb_to_verb_variables = {}

		self.processor = DocumentProcessor(is_tac, self.indicator_matrix)

	def build_compatibility_matrix(self):
		for np in self.noun_phrases:
			for vp in self.verb_phrases:
				related = self.check_relation(np, vp, self.noun_phrases, self.alternative_NPs)
				
				if not related:
					related = self.check_relation(vp, np, self.verb_phrases, self.alternative_VPs)

				if not related and (np, vp) in self.indicator_matrix:
					related = True

				self.compatibility_matrix[(np, vp)] = int(related)

	def check_relation(phrase1, phrase2, other_phrase1s, alt_phrase1s):
		for other_phrase1 in other_phrase1s:
			if (phrase1, other_phrase1) in alt_phrase1s \
			and (other_phrase1, phrase2) in self.indicator_matrix:
				return True
		return False

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
				for j in range(i + 1, len_alt_phrases):
					phrase1 = alt_phrases[i]
					phrase2 = alt_phrases[j]
					self.alternative_NPs[(phrase1, phrase2)] = 1
					self.alternative_NPs[(phrase2, phrase1)] = 1

	def find_alt_VPs(self, verb_phrases):
		len_verb_phrases = len(verb_phrases)
		for i in range(0, len_alt_phrases - 1):
			for j in range(i + 1, len_alt_phrases):
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

	def update_model(self):
		self.noun_phrases = self.processor.noun_phrases
		self.verb_phrases = self.processor.verb_phrases
		self.all_phrases = self.processor.all_phrases
		self.corefs = self.processor.corefs
		self.nouns = self.processor.nouns
		self.verbs = self.processor.verbs
		self.docs = self.processor.docs

	def generate_summary(self):
		self.score_phrases()
		self.find_optimal_solution()

	def process_document(self, string):
		self.processor.process_document(string)
