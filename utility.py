from nltk.corpus import stopwords

stopwords = set(stopwords.words('english'))

# Tokens must be stripped
def remove_stopwords(tokens):
	return [token for token in tokens if token not in stopwords]