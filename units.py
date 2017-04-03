from corenlp_pywrap import pywrap
import xml.etree.ElementTree
import utility
import re

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

	def __contains__(self, phrase_tuple):
		return super().__contains__(self.__transformkey__(phrase_tuple))
		
	def __getitem__(self, phrase_tuple):
		assert isinstance(phrase_tuple, tuple)
		assert len(phrase_tuple) == 2
		assert isinstance(phrase_tuple[0], Phrase)
		assert isinstance(phrase_tuple[1], Phrase)

		return super().__getitem__(self.__transformkey__(phrase_tuple))

	def __setitem__(self, phrase_tuple, value):
		assert isinstance(phrase_tuple, tuple)
		assert len(phrase_tuple) == 2
		assert isinstance(phrase_tuple[0], Phrase)
		assert isinstance(phrase_tuple[1], Phrase)

		super().__setitem__(self.__transformkey__(phrase_tuple), value)

	def __transformkey__(self, phrase_tuple):
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
		return key


class InputDocument():
	__p_marker = '\n\n'

	def __init__(self, input_str, is_tac=True):
		full_annotator_list = ["tokenize", "ssplit", "pos", "lemma", "ner", "parse", "dcoref"]
		cn = pywrap.CoreNLP(url='http://localhost:9000', annotator_list=full_annotator_list)
		
		if is_tac:
			text = self.parse_xml_string(input_str)
		else:
			text = input_str

		# Note: corenlp recognizes sentences delimiters as periods regardless of newlines
		result = cn.basic(text, out_format='json').json()
		# CAUTION: sentences may not coincide with the number of sentences in parse_trees
		self.sentences = utility.sent_tokenize(text)
		self.parse_trees = [sentence['parse'] for sentence in result['sentences']]
		self.named_entities = self.extract_named_entities(result)
		self.corefs = self.extract_coreferences(result)
		self.word_to_lemma_dict = self.build_word_to_lemma_dict(result)
		self.paragraphs = self.prepare_paragraphs(text, result)

	def parse_xml_string(self, xml_string):
		root = xml.etree.ElementTree.fromstring(xml_string)
		self.headline = root.find('.//HEADLINE').text.strip()
		text = ''
		# To replace \n in line breaks within <P> tag
		# Note: Minor issue with with 16\n-year-old --> 16 -year-old
		newline_regex = re.compile('\n')
		for child in root.find('.//TEXT'):
			if child.tag == 'P':
				text += newline_regex.sub(' ', child.text.strip()) + self.__class__.__p_marker
		return text.strip()

	def extract_named_entities(self, result):
		named_entities = []
		prev_token_ner_type = None
		ner_string = ''
		for sentence in result['sentences']:
			for token in sentence['tokens']:
				if token['ner'] != 'O':
					# New NER
					if prev_token_ner_type == None:
						ner_string = token['originalText']
						prev_token_ner_type = token['ner']
					# Token belongs to previous NER
					elif token['ner'] == prev_token_ner_type:
						ner_string += ' ' + token['originalText']
					# Token belongs to a new NER
					else:
						named_entities.append(ner_string.strip())
						ner_string = token['originalText']
						prev_token_ner_type = token['ner']
				else:
					# Token is no longer part of NER
					if prev_token_ner_type != None:
						named_entities.append(ner_string.strip())
						prev_token_ner_type = None
						ner_string = ''
		return named_entities

	def extract_coreferences(self, result):
		corefs = {}

		for coref_chain in result['corefs'].values():
			if len(coref_chain) == 1:
				continue

			mentions_set = set()
			for mention in coref_chain:
				mentions_set.add(mention['text'])
				if mention['isRepresentativeMention']:
					representative_mention = mention

			corefs[representative_mention['text']] = mentions_set

		return corefs

	def build_word_to_lemma_dict(self, result):
		tokens = [token for sentence in result['sentences'] for token in sentence['tokens']]
		tokens = utility.remove_stopwords(tokens, 'originalText')

		word_to_lemma_dict = {}
		for token in tokens:
			word_to_lemma_dict[token['originalText']] = token['lemma']

		return word_to_lemma_dict
		
	def prepare_paragraphs(self, text, result):
		paragraphs = []
		paragraphs_text = text.split(self.__class__.__p_marker)
		for paragraph_text in paragraphs_text:
			paragraph_concept_frequency = self.extract_concepts_from_string(paragraph_text)
			paragraph = Paragraph(paragraph_concept_frequency)
			paragraphs.append(paragraph)
		
		return paragraphs

	def get_sentences(self, text):
		return utility.sent_tokenize(text)

	def extract_concepts_from_string(self, string):
		concept_frequency_dict = {}

		# Consider using Counter class as optimization
		tokens = utility.word_tokenize(string)
		encountered = set()
		lemma_unigrams = []
		for token in tokens:
			if token in self.word_to_lemma_dict:
				lemma = self.word_to_lemma_dict[token]
				if lemma not in encountered:
					encountered.add(lemma)
					lemma_unigrams.append(lemma)
				utility.increment_value(concept_frequency_dict, lemma)

		# Note: Bigrams are generated from ordered unique lemmas not original string
		lemma_bigrams = utility.generate_bigrams(lemma_unigrams)
		for bigram in lemma_bigrams:
			utility.increment_value(concept_frequency_dict, bigram)

		# Note: Named entities may duplicate with unigrams or bigrams as they are in un-preprocessed form
		for entity in self.named_entities:
			if entity in string:
				utility.increment_value(concept_frequency_dict, entity)

		return concept_frequency_dict
