from flask import Flask, request, jsonify
import os
import summarizer

app = Flask(__name__)
path = os.path.dirname(__file__)
app = Flask(__name__, static_folder='server/static')

@app.route('/')
def home():
	return app.send_static_file('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
	texts = request.form['texts']
	summary = summarizer.summarize(texts)

	return summary


if __name__ == '__main__':
	app.run(host='0.0.0.0')