import math

class PhraseScorer():
	B = 6.0
	RHO = 0.5
	
	def __init__(self, input_doc):
		self.input_document = input_doc
		
	def weighting_paragraph(self, paragraph_position):
		if paragraph_position < -1 * math.log(self.B) / math.log(self.RHO):
			return math.pow(self.RHO, paragraph_position) * self.B
		else:
			return 1.0
		
	def score_phrase(self, phrase):
		score = 0.0
		concepts = phrase.concepts
		paragraphs = self.input_document.paragraphs
		len_paragraph = len(paragraphs)
		for concept in concepts:
			for i in range(len_paragraph):
				count = paragraphs[i].count_frequency(concept)
				score += count * self.weighting_paragraph(i)
			
		return score