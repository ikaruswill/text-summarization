from nltk.util import ngrams

def load_file(file_path):
	with open(file_path, 'r') as f:
		text = f.read()
	return text

def count_words(text):
	return len(text.split())

def generate_unigrams(text):
	return list(ngrams(text.lower(), 1))

def generate_bigrams(text):
	return list(ngrams(text.lower(), 2))

def split_string_to_words(text):
	return text.split()

def increment_value(self, dictionary, key):
	if key not in dictionary:
		dictionary[key] = 0
	dictionary[key] += 1