from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def load_file(file_path):
	with open(file_path, 'r') as f:
		text = f.read()
	return text

def count_words(text):
	return len(text.split())

def tokenize(text):
	return word_tokenize(text)

def generate_bigrams(tokens):
	return [' '.join(bigram) for bigram in ngrams(tokens, 2)]

def remove_stopwords(tokens, key):
	stopwords_set = set(stopwords.words('english'))
	return [token for token in tokens if token[key] not in stopwords_set]

def increment_value(dictionary, key):
	if key not in dictionary:
		dictionary[key] = 0
	dictionary[key] += 1
