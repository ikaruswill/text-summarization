import xml.etree.ElementTree

class InputDocument(object):
	def __init__(self, input_str, isTAC=True):
		full_annotator_list = ["tokenize", "ssplit", "pos", "lemma", "ner", "parse", "dcoref"]
		cn = pywrap.CoreNLP(url='http://localhost:9000', annotator_list=full_annotator_list)
		
		if isTAC:
			text = parse_xml_string(input_str)
		else:
			text = input_str

		result = cn.basic(text, out_format='json')
		extract_named_entities(result)
		extract_coreferences(result)
		build_word_to_lemma_dict(result)
		prepare_paragraphs(result)

	def parse_xml_string(self, xml_string):
		root = xml.etree.ElementTree.fromstring(xml_string)
		self.headline = root.find('.//HEADLINE')
		text = ''
		for child in root.find('.//TEXT'):
			if child.tag == 'P':
				text += child.text
				text += '\n'
		return text

	def extract_named_entities(self, result):
		self.named_entities = []
		for sentence in result:
			for token in sentence['tokens']:
				if token['ner'] != 'O':
					self.named_entities.append(token['originalText'])

	def extract_coreferences(self, result):
		pass

	def build_word_to_lemma_dict(self, result):
		tokens = [token for sentence in result for token in sentence['tokens']]
		tokens = remove_stopwords(tokens, 'originalText')

		self.word_to_lemma_dict = {}
		for token in tokens:
			self.word_to_lemma_dict[token['orignalText']] = token['lemma']
		
	def prepare_paragraphs(self, result):
		pass

