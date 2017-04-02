import argparse
import os
import utility
from parser import Parser

DEFAULT_MAXIMUM_SENTENCE = 10
DEFAULT_ALTERNATIVE_VP_THRESHOLD = 0.75
DEFAULT_MAX_WORD_LENGTH = 100
DEFAULT_THREADS = 0

def main():
	parser = Parser(args.max_sent, args.alt_vp_thresh, args.max_word_length, not args.plaintext, args.threads)
	for dirpath, dirnames, filenames in os.walk(args.input_dir):
		for filename in filenames:
			if filename.startswith('.'):
				continue
			file_path = os.path.join(dirpath, filename)
			text = utility.load_file(file_path)
			parser.process_document(text)

		parser.update_model()
		summary = parser.generate_summary()
		print(summary)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Abstractive Summarizer')
	parser.add_argument('input_dir', help='input folder containing all text files')
	parser.add_argument('output_file', help='output file')
	parser.add_argument('-w', '--max-word-length', help='maximum word length', default=DEFAULT_MAX_WORD_LENGTH)
	parser.add_argument('-v', '--alt-vp-thresh', help='alternative VP threshold', default=DEFAULT_ALTERNATIVE_VP_THRESHOLD)
	parser.add_argument('-s', '--max-sent', help='maximum number of sentences', default=DEFAULT_MAXIMUM_SENTENCE)
	parser.add_argument('-t', '--threads', help='number of threads', default=DEFAULT_THREADS)
	parser.add_argument('-p', '--plaintext', help='is plain text data', default=False, action='store_true')
	parser.add_argument('-e', '--export-only', help='only export the phrases', default=False, action='store_true')
	args = parser.parse_args()

	main()