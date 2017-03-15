from nltk.util import ngrams

def count_words(text):
	return len(text.split())

def generate_unigrams(text):
	return list(ngrams(text.lower(), 1))

def generate_bigrams(text):
	return list(ngrams(text.lower(), 2))

def split_string_to_words(text):
	return text.split()
