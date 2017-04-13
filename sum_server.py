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

def crawl(urls):
	results = []
	for url in urls:
		crawler = Crawler(depth=1)
		crawler.crawl(url)
		results.append(crawler.content[url])
	return results

@app.route('/summarize', methods=['POST'])
def summarize():
	urls = request.get_json()
	texts = crawl(urls[0:5])
	print(texts)
	summary = summarizer.summarize(texts)
	print(summary)
	return summary


if __name__ == '__main__':
	app.run(host='0.0.0.0')