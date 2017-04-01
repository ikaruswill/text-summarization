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

	def calculate_jaccard_index(phrase1, phrase2):
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