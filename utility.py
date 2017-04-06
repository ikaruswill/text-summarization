from nltk.util import ngrams
import nltk.tokenize
from nltk.corpus import stopwords
import math

def load_file(file_path):
	with open(file_path, 'r') as f:
		text = f.read()
	return text

def count_words(text):
	return len(text.split())

def word_tokenize(text):
	return nltk.tokenize.word_tokenize(text)

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

def calculate_cosine_similarity(phrase1, phrase2):
	concepts_phrase1 = phrase1.concepts
	concepts_phrase2 = phrase2.concepts
	if len(concepts_phrase1) == 0 or len(concepts_phrase2) == 0:
		return 0.0
	product = 0.0
	for concept, freq in concepts_phrase1.items():
		if concept in concepts_phrase2:
			product += freq * concepts_phrase2[concept]

	return product / calculate_phrase_magnitude(phrase1) * calculate_phrase_magnitude(phrase2)

def calculate_phrase_magnitude(phrase):
	sum_squares = 0
	for freq in phrase.concepts.values():
		sum_squares += math.pow(freq, 2)

	return math.sqrt(sum_squares)

def generate_filename(dirname):
	dirname_split = dirname.split('-')
	dataset = dirname_split[1]
	topic = dirname_split[0][-1]
	documentset = dirname_split[0][:-1]

	return documentset + '-' + dataset + '.M.100.' + topic + '.1'