class Parser():

	def __init__(self):
		pass

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