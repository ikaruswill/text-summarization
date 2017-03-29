import utility

class Phrase():
	content = None
	is_NP = True
	score = 0.0
	parent_id = -1
	sentence_node_id = 0
	phrase_id = None

	sentence_length = 0

	_np_id = 0
	_vp_id = 0
	pronouns = ["it", "i", "you", "he", "they", "we", "she", "who", "them", "me", "him", "one", "her", "us", "something", "nothing", "anything", "himself", "everything", "someone", "themselves", "everyone", "itself", "anyone", "myself"]
	
	concepts = set()

	def __init__(self, content, is_NP, parent_id=-1, sentence_node_id=0):
		self.content = content
		self.is_NP = is_NP
		self.parent_id = parent_id
		self.sentence_node_id = sentence_node_id
		if is_NP:
			phrase_id = _np_id
			_np_id += 1
		else:
			id = _vp_id
			_vp_id += 1

	def __repr__(self):
		return self.content + ": " + self.score

	def __eq__(self, phrase):
		return self.content == phrase

	def get_content(self):
		return self.content

	def setContent(self, content):
		self.content = content

	def is_NP(self):
		return self.is_NP

	def set_score(self, value):
		self.score = value

	def get_score(self):
		if self.score is not None:
			return self.score
		else:
			print("What the hell", self)

	def get_id(self):
		return self.phrase_id

	def set_concepts(self, concepts):
		self.concepts = concepts

	def generate_concepts(self):
		if self.concepts:
			return
		# TODO

	def get_concepts(self):
		if not self.concepts:
			self.generateConcepts()

		return concepts

	def get_parent_id(self):
		return self.parent_id

	def get_sentence_length(self):
		return self.sentence_length

	def set_sentence_length(self, value):
		self.sentence_length = value

	def is_pronoun(self):
		return self.is_NP and this.content.lower() in pronouns

	def get_word_length(self):
		return utility.count_words(self.content)

	def get_sentence_node_id(self):
		return self.sentence_node_id

class Paragraph():
	doc = None #annotation, null
	tokens = [] #list of labels, null
	concept_frequency = {}

	def __init__(self, concept_frequency):
		self.concept_frequency = concept_frequency

	def get_concepts(self):
		return self.concept_frequency.keys()

	def count_frequency(self, concept):
		if concept in concept_frequency:
			return concept_frequency[concept]
		else:
			return 0

def main():
	t = "This is my question; what   _ yeah"
	p = Phrase(t, False)
	print(p.get_word_length())

	print(repr(t.split()))

if __name__ == '__main__':
	main()
