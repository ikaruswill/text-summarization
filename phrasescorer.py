import math

class PhraseScorer():
	B = 6.0
	RHO = 0.5
	
	def _init_(self, input_doc):
		self.input_document = input_doc
		
	def weighting_paragraph(self, paragraph_position):
		if paragraph_position < -1 * math.log(B) / math.log(RHO):
			return math.pow(RHO, paragraph_position) * B
		else:
			return 1.0
		
	def score_phrase(self, phrase):
		score = 0.0
		concept = phrase.concepts
		paragraphs = input_document.paragraphs
		paragraphLength = len(paragraphs)
		for concept in concepts:
			for i in range(paragraghLength):
				count = paragraphs[i].count_frequency(concept)
				score += count * self.weighting_paragraph(i)
			
		return score