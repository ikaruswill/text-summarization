from corenlp_pywrap import pywrap
from preprocess import remove_stopwords
import xml.etree.ElementTree
from units import Paragraph
import utility

class InputDocument(object):
	def __init__(self, input_str, isTAC=True):
		full_annotator_list = ["tokenize", "ssplit", "pos", "lemma", "ner", "parse", "dcoref"]
		cn = pywrap.CoreNLP(url='http://localhost:9000', annotator_list=full_annotator_list)
		
		if isTAC:
			text = self.parse_xml_string(input_str)
		else:
			text = input_str

		result = cn.basic(text, out_format='json').json()
		self.named_entities = self.extract_named_entities(result)
		self.coreferences = self.extract_coreferences(result)
		self.word_to_lemma_dict = self.build_word_to_lemma_dict(result)
		self.paragraphs = self.prepare_paragraphs(text, result)

	def parse_xml_string(self, xml_string):
		root = xml.etree.ElementTree.fromstring(xml_string)
		self.headline = root.find('.//HEADLINE')
		text = ''
		for child in root.find('.//TEXT'):
			if child.tag == 'P':
				text += child.text
		return text

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
		tokens = remove_stopwords(tokens, 'originalText')

		word_to_lemma_dict = {}
		for token in tokens:
			word_to_lemma_dict[token['originalText']] = token['lemma']

		return word_to_lemma_dict
		
	def prepare_paragraphs(self, text, result):
		paragraphs = []
		paragraphs_text = text.split('\n')
		for paragraph_text in paragraphs_text:
			paragraph_concept_frequency = self.extract_concepts_from_string(paragraph_text)
			paragraph = Paragraph(paragraph_concept_frequency)
			paragraphs.append(paragraph)
		
		return paragraphs

	def extract_concepts_from_string(self, string):
		concept_frequency_dict = {}

		# Consider using Counter class as optimization
		unigrams = utility.generate_unigrams(string)
		filtered_unigrams = set()
		for unigram in unigrams:
			if unigram in self.word_to_lemma_dict:
				lemma = self.word_to_lemma_dict[unigram]
				filtered_unigrams.add(lemma)
				utility.increment_value(concept_frequency_dict, lemma)

		bigrams = utility.generate_bigrams(string)
		for bigram in bigrams:
			utility.increment_value(concept_frequency_dict, bigram)

		for entity in self.named_entities:
			if entity in string:
				utility.increment_value(concept_frequency_dict, entity)

		return concept_frequency_dict
