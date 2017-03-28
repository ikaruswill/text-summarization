from nltk.corpus import stopwords

stopwords = set(stopwords.words('english'))

# Tokens must be stripped
def remove_stopwords(tokens, key):
	return [token for token in tokens if token[key] not in stopwords]
