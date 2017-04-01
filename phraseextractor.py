

class PhraseExtractor():
	def __init__(self, input_document, phrase_matrix):
		self.input_document = input_document
		self.phrase_matrix = phrase_matrix

	def extract_all_phrases(self):
		all_phrases = []
		sentences = input_document.sentences

		for sentence in sentences:
			phrases_in_sentence = extract_phrases(sentence)

			# ADD ALL PHRASES FROM PHRASES IN SENTENCE

			# SET INDICATOR MATRIX
		


