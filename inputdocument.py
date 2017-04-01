from corenlp_pywrap import pywrap
import xml.etree.ElementTree
from units import Paragraph
import utility
import re

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
		self.named_entities = self.extract_named_entities(result)
		self.coreferences = self.extract_coreferences(result)
		self.word_to_lemma_dict = self.build_word_to_lemma_dict(result)
		self.paragraphs = self.prepare_paragraphs(text, result)
		self.sentences = self.sent_tokenize(text)

	def parse_xml_string(self, xml_string):
		root = xml.etree.ElementTree.fromstring(xml_string)
		self.headline = root.find('.//HEADLINE').text
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
		for sentence in result['sentences']:
			for token in sentence['tokens']:
				if token['ner'] != 'O':
					named_entities.append(token['originalText'])
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
