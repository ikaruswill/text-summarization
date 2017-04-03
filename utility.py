from nltk.util import ngrams
import nltk.tokenize
from nltk.corpus import stopwords

def load_file(file_path):
	with open(file_path, 'r') as f:
		text = f.read()
	return text

def count_words(text):
	return len(text.split())

def word_tokenize(text):
	return nltk.tokenize.word_tokenize(text)

def sent_tokenize(text):
	return nltk.tokenize.sent_tokenize(text)

def generate_bigrams(tokens):
	return [' '.join(bigram) for bigram in ngrams(tokens, 2)]

def remove_stopwords(tokens, key):
	stopwords_set = set(stopwords.words('english'))
	return [token for token in tokens if token[key] not in stopwords_set]

def increment_value(dictionary, key):
	if key not in dictionary:
		dictionary[key] = 0
	dictionary[key] += 1

def build_key(phrase1, phrase2):
		return str(phrase1.phrase_id) + ':' + str(phrase2.phrase_id)

def calculate_jaccard_index(phrase1, phrase2):
	concepts_phrase1 = phrase1.concepts
	concepts_phrase2 = phrase2.concepts

	count = 0
	for concept in concepts_phrase1:
		if concept in concepts_phrase2:
			count += 1

	divisor = len(concepts_phrase1) + len(concepts_phrase2) - count
	
	if divisor == 0:
		return 0.0
	else:
		return float(count) / divisor