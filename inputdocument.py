from corenlp_pywrap import pywrap
from preprocess import remove_stopwords
import xml.etree.ElementTree

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
		self.extract_coreferences(result)
		self.word_to_lemma_dict = self.build_word_to_lemma_dict(result)
		self.prepare_paragraphs(result)

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
		pass

	def build_word_to_lemma_dict(self, result):
		tokens = [token for sentence in result['sentences'] for token in sentence['tokens']]
		tokens = remove_stopwords(tokens, 'originalText')

		word_to_lemma_dict = {}
		for token in tokens:
			word_to_lemma_dict[token['originalText']] = token['lemma']

		return word_to_lemma_dict
		
	def prepare_paragraphs(self, result):
		pass

