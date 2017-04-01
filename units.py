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
			self.phrase_id = self._np_id
			self._np_id += 1
		else:
			self.phrase_id = self._vp_id
			self._vp_id += 1

	def __repr__(self):
		return self.content + ": " + self.score

	def __eq__(self, phrase):
		return self.content == phrase

	def generate_concepts(self):
		if self.concepts:
			return
		# TODO

	def get_concepts(self):
		if not self.concepts:
			self.generateConcepts()

		return concepts

	@property
	def is_pronoun(self):
		return self.is_NP and this.content.lower() in pronouns

	@property
	def word_length(self):
		return utility.count_words(self.content)

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

class PhraseMatrix(dict):
	def __init__(self, *args):
		super().__init__(self, *args)

	def __getitem__(self, phrase_tuple):
		assert isinstance(phrase_tuple, tuple)
		assert len(phrase_tuple) == 2
		assert isinstance(phrase_tuple[0], Phrase)
		assert isinstance(phrase_tuple[1], Phrase)
		
		key = ''
		if phrase_tuple[0].is_NP:
			key += 'NP_'
		else:
			key += 'VP_'

		key += str(phrase_tuple[0].phrase_id) + ':'

		if phrase_tuple[1].is_NP:
			key += 'NP_'
		else:
			key += 'VP_'

		key += str(phrase_tuple[1].phrase_id)

		return super().__getitem__(key)

	def __setitem__(self, phrase_tuple, value):
		assert isinstance(phrase_tuple, tuple)
		assert len(phrase_tuple) == 2
		assert isinstance(phrase_tuple[0], Phrase)
		assert isinstance(phrase_tuple[1], Phrase)
		
		key = ''
		if phrase_tuple[0].is_NP:
			key += 'NP_'
		else:
			key += 'VP_'

		key += str(phrase_tuple[0].phrase_id) + ':'

		if phrase_tuple[1].is_NP:
			key += 'NP_'
		else:
			key += 'VP_'

		key += str(phrase_tuple[1].phrase_id)

		super().__setitem__(key, value)