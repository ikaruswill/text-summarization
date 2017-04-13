from flask import Flask, request, jsonify
import os
import summarizer
from crawler import Crawler
from urllib.parse import urlparse


# path = os.path.dirname(__file__)
app = Flask(__name__, static_folder='server/static')

@app.route('/')
def home():
	return app.send_static_file('index.html')

@app.route('/crawl', methods=['POST'])
def crawl():
	urls = request.get_json()
	crawler = Crawler(depth=1)
	for url in urls:
		domain = urlparse(url).netloc
		crawler.crawl(url)
		print(crawler.content[domain].keys())
	pass


@app.route('/summarize', methods=['POST'])
def summarize():
	texts = request.get_json()
	summary = summarizer.summarize(texts)

	return summary


if __name__ == '__main__':
	app.run(host='0.0.0.0')