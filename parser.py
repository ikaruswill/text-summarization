from corenlp_pywrap import pywrap
from preprocess import remove_stopwords

class Parser(object):

	def __init__(self, text, path):
		full_annotator_list = ["tokenize", "ssplit", "pos", "lemma", "ner", "parse", "dcoref"]
		cn = pywrap.CoreNLP(url='http://localhost:9000', annotator_list=full_annotator_list)
		self.text = text
		result = cn.basic(text, out_format='json')
		extract_named_entities(result)
		extract_coreferences(result)
		build_word_to_lemma_dict(result)
		prepare_paragraphs(result)

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

