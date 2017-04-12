import argparse
import os
import utility
from parser import Parser

DEFAULT_MAXIMUM_SENTENCE = 10
DEFAULT_ALTERNATIVE_VP_THRESHOLD = 0.75
DEFAULT_MAX_WORD_LENGTH = 100
DEFAULT_THREADS = 0

def summarize(texts):
	for text in texts:
		parser = Parser(DEFAULT_MAXIMUM_SENTENCE, DEFAULT_ALTERNATIVE_VP_THRESHOLD, DEFAULT_MAX_WORD_LENGTH, False, threads=0)
		parser.process_document(text)

	parser.update_model()
	return parser.generate_summary()

def main():
	for dirpath, dirnames, filenames in os.walk(args.input_dir):
		print('In:', dirpath)
		parser = Parser(args.max_sent, args.alt_vp_thresh, args.max_word_length, not args.plaintext, args.threads)
		found_data = False
		for filename in filenames:
			if filename.startswith('.') or not os.path.splitext(filename)[1].startswith('.LDC'):
				print('Ignore:', filename)
				continue
			found_data = True
			file_path = os.path.join(dirpath, filename)
			text = utility.load_file(file_path)
			print('Process:', file_path)
			parser.process_document(text)
			
		if found_data:
			dirname = os.path.split(dirpath)[-1]
			print('Found data, processing...')
			parser.update_model()
			summary = parser.generate_summary()
			print('Summary: ')
			print(summary)

			with open(os.path.join(args.output_dir, utility.generate_filename(dirname)), 'w') as f:
				f.write(summary)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Abstractive Summarizer')
	parser.add_argument('input_dir', help='input folder containing all text files')
	parser.add_argument('output_dir', help='output directory')
	parser.add_argument('-w', '--max-word-length', help='maximum word length', default=DEFAULT_MAX_WORD_LENGTH)
	parser.add_argument('-v', '--alt-vp-thresh', help='alternative VP threshold', default=DEFAULT_ALTERNATIVE_VP_THRESHOLD)
	parser.add_argument('-s', '--max-sent', help='maximum number of sentences', default=DEFAULT_MAXIMUM_SENTENCE)
	parser.add_argument('-t', '--threads', help='number of threads', default=DEFAULT_THREADS)
	parser.add_argument('-p', '--plaintext', help='is plain text data', default=False, action='store_true')
	parser.add_argument('-e', '--export-only', help='only export the phrases', default=False, action='store_true')
	args = parser.parse_args()

	main()