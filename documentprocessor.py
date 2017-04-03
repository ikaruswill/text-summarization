from phraseextractor import PhraseExtractor
from units import InputDocument

class DocumentProcessor():
	def __init__(self, is_tac, indicator_matrix):
		self.indicator_matrix = indicator_matrix
		self.is_tac = is_tac
		self.docs = []
		self.noun_phrases = []
		self.verb_phrases = []
		self.all_phrases = []

		self.nouns = []
		self.verbs = []
		self.corefs = {}

	def process_document(self, text):
		doc = InputDocument(text)
		self.docs.append(doc)
		self.extract_phrases(doc)
		self.corefs.update(doc.corefs)

	def extract_phrases(self, doc):
		phrase_extractor = PhraseExtractor(doc, self.indicator_matrix)
		phrases = phrase_extractor.extract_all_phrases()

		for phrase in phrases:
			if phrase.is_NP:
				self.noun_phrases.append(phrase)
				self.nouns.append(phrase.content)
			else:
				self.verb_phrases.append(phrase)
				self.verbs.append(phrase.content)
			self.all_phrases.append(phrase)