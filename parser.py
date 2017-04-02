from units import PhraseMatrix
from documentprocessor import DocumentProcessor
import gurobipy as g
import sys
import argparse
import os

DEFAULT_MAXIMUM_SENTENCE = 10;
DEFAULT_ALTERNATIVE_VP_THRESHOLD = 0.75;
DEFAULT_MAX_WORD_LENGTH = 100;

class Parser():
	MIN_SENTENCE_LENGTH = 5;
	MINIMUM_VERB_LENGTH = 2;

	def __init__(self, max_sentence, alternative_vp_threshold, max_word_length, is_TAC, threads=1):
		self.max_sentence = max_sentence
		self.alternative_vp_threshold = alternative_vp_threshold
		self.max_word_length = max_word_length
		self.threads = threads

		self.indicator_matrix = PhraseMatrix()
		self.compatibility_matrix = PhraseMatrix()
		self.alternative_VPs = PhraseMatrix()
		self.alternative_NPs = PhraseMatrix()

		self.noun_phrases = []
		self.verb_phrases = []
		self.all_phrases = []
		self.corefs = {}

		self.nouns = set()
		self.verbs = set()

		self.docs = []

		self.noun_variables = {}
		self.verb_variables = {}
		self.gamma_variables = {}
		self.noun_to_noun_variables = {}
		self.verb_to_verb_variables = {}

		self.processor = DocumentProcessor()

	def build_compatibility_matrix(self):
		for np in self.noun_phrases:
			for vp in self.verb_phrases:
				related = self.check_relation(np, vp, self.noun_phrases, self.alternative_NPs)
				
				if not related:
					related = self.check_relation(vp, np, self.verb_phrases, self.alternative_VPs)

				if not related and (np, vp) in self.indicator_matrix:
					related = True

				self.compatibility_matrix[(np, vp)] = int(related)

	def check_relation(phrase1, phrase2, other_phrase1s, alt_phrase1s):
		for other_phrase1 in other_phrase1s:
			if (phrase1, other_phrase1) in alt_phrase1s \
			and (other_phrase1, phrase2) in self.indicator_matrix:
				return True
		return False

	def calculate_similarity(self, phrase1, phrase2):
		for coref_set in self.corefs.values():
			if a.content in coref_set and b.content in coref_set:
				return 1.0

		return self.calculate_jaccard_index(phrase1, phrase2)

	def calculate_jaccard_index(self, phrase1, phrase2):
		concepts_phrase1 = phrase1.concepts
		concepts_phrase2 = phrase2.concepts

		count = 0
		for concept in concepts_phrase1:
			if concepts_phrase2.find(concept):
				count += 1

		divisor = len(concepts_phrase1) + len(concepts_phrase2) - count
		
		if divisor == 0:
			return 0.0
		else:
			return float(count) / divisor

	def score_phrases(self):
		for doc in self.docs:
			scorer = PhraseScorer(doc)
			for phrase in self.all_phrases:
				score = scorer.score_phrases(phrase)
				phrase.score += score

	def find_alt_NPs(self, noun_phrases, clusters):
		for cluster in clusters:
			alt_phrases = []

			for phrase_text in cluster:
				for phrase in noun_phrases:
					if phrase.content == phrase_text:
						alt_phrases.append(phrase)

			len_alt_phrases = len(alt_phrases)
			for i in range(0, len_alt_phrases - 1):
				for j in range(i + 1, len_alt_phrases):
					phrase1 = alt_phrases[i]
					phrase2 = alt_phrases[j]
					self.alternative_NPs[(phrase1, phrase2)] = 1
					self.alternative_NPs[(phrase2, phrase1)] = 1

	def find_alt_VPs(self, verb_phrases):
		len_verb_phrases = len(verb_phrases)
		for i in range(0, len_alt_phrases - 1):
			for j in range(i + 1, len_alt_phrases):
				phrase1 = verb_phrases[i]
				phrase2 = verb_phrases[j]

				d = calculate_jaccard_index(phrase1, phrase2)
				if d >= self.alternative_vp_threshold:
					self.alternative_VPs[(phrase1, phrase2)] = d
					self.alternative_VPs[(phrase2, phrase1)] = d

	def start_optimization(self):
		env = g.Env()
		env.Params.Threads = self.threads
		model = g.Model(env=env)

		expr = g.LinExpr()

		for np in self.noun_phrases:
			var = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "n:" + noun.phrase_id)
			noun_variables[noun.phrase_id] = var
			expr.addTerm(noun.score, var)

			for vp in self.verb_phrases:
				if compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + self.build_key(np, vp)
					gamma = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, key)

					gamma_variables[key] = gamma

		for vp in self.verb_phrases:
			var = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "v:" + verb.phrase_id)
			verb_variables[vp.phrase_id] = var
			expr.addTerm(vp.score, var)

		len_noun_phrases = len(self.noun_phrases)
		for i in range(0, len_noun_phrases - 1):
			for j in range(i + 1, len_noun_phrases):
				np1 = self.noun_phrases[i]
				np2 = self.noun_phrases[j]
				key = self.build_key(np1, np2)

				var = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "n2n:" + key)
				noun_to_noun_variables[key] = var
				score = -(np1.score + np2.score) * self.calculate_similarity(np1, np2)
				expr.addTerm(score, var)

		len_verb_phrases = len(self.verb_phrases)
		for i in range(0, len_verb_phrases - 1):
			for j in range(i + 1, len_verb_phrases):
				vp1 = self.verb_phrases[i]
				vp2 = self.verb_phrases[j]
				key = self.build_key(vp1, vp2)

				var = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "v2v:" + key)
				verb_to_verb_variables[key] = var
				score = -(vp1.getScore() + vp2.getScore()) * self.calculate_similarity(vp1, vp2)
				expr.addTerm(score, var)

		model.update()
		model.setObjective(expr, GRB.MAXIMIZE)

		# Add constraints
		add_NP_validity(model)
		add_VP_validity(model)
		add_not_I_within_I(model, self.noun_phrases, self.noun_variables)
		add_not_I_within_I(model, self.verb_phrases, self.verb_variables)
		add_phrase_cooccurence(model, self.noun_phrases, self.noun_variables, self.noun_to_noun_variables)
		add_phrase_cooccurence(model, self.verb_phrases, self.verb_variables, self.verb_to_verb_variables)
		add_sentence_number(model, self.max_sentence)
		add_short_sentence_avoidance(model, self.MIN_SENTENCE_LENGTH)
		add_pronoun_avoidance(model)
		add_length(model)

		model.optimize()

		selected_nouns = {}
		selected_verbs = {}

		for np in self.noun_phrases:
			var = noun_variables[np.phrase_id]
			selected = var.X

			if selected > 0:
				selected_nouns[np.phrase_id] = phrase

		for vp in self.verb_phrases:
			var = verb_variables[vp.phrase_id]
			selected = var.X

			if selected > 0:
				selected_verbs[vp.phrase_id] = phrase

		selected_NP_lists = {}
		summary_sentences = {} # Sorted

		for key, var in gamma_variables.items():
			value = var.X

			if value > 0:
				data = key.split(':')
				noun_id = int(data[0])
				verb_id = int(data[1])

				if not noun_id in selected_NP_lists:
					selected_NP_lists[noun_id] = []

				selected_NP_lists[noun_id].append(selected_verbs[verb_id])

		summary = ""

		for key, np_list in selected_NP_lists:
			np = selected_nouns[key]
			sentence = np.content + " "
			min_id = sys.maxsize

			verbs = []
			self.phrases.sort(key=lambda x: operator.attrgetter('phrase_id'))

			for phrase in self.phrases:
				if not phrase.is_NP and min_id > phrase.phrase_id:
					mind_id = phrase.phrase_id
				verbs.append(phrase.content)

			sentence += ', '.join(verbs)
			summary_sentences[min_id] = sentence

		for key, sentence in sorted(summary_sentences.items()):
			summary += sentence + '\n'

		return summary

	def add_NP_validity_constraint(self, model):
		for np in self.noun_phrases:
			np_var = self.noun_variables[np.phrase_id]
			constraint = LinExpr()

			for vp in self.verb_phrases:
				if self.compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + self.build_key(np, vp)
					var = self.gamma_variables[key]

					expr = LinExpr()
					expr.addTerms(1.0, np_var)
					expr.addTerms(-1.0, var)

					model.addConstr(expr, GRB.GREATER_EQUAL, 0.0, 'np_validity:' + noun.phrase_id)

					constraint.addTerms(1.0, var)

			constraint.addTerms(-1.0, np_var)
			model.addConstr(constraint, GRB.GREATER_EQUAL, 0.0, 'np_validity:' + noun.phrase_id)

	def add_VP_validity_constraint(self, model):
		for vp in self.verb_phrases:
			vp_var = self.verb_variables[vp.phrase_id]
			constraint = LinExpr()
			contraint.addTerms(-1.0, vp_var)

			for np in self.noun_phrases:
				if self.compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + self.build_key(np, vp)
					var = self.gamma_variables[key]

					contraint.addTerms(1.0, var)

			model.addConstr(constr, GRB.EQUAL, 0.0, 'vp_legality:' + vp.phrase_id)

	def add_not_I_within_I_constraint(model, phrases, variables):
		len_phrases = len(phrases)
		for i in range(0, len_phrases - 1):
			for j in range(i + 1, len_phrases):
				phrase1 = phrases[i]
				phrase2 = phrases[j]
				if phrase1.phrase_id == phrase.parent_id:
					var1 = variables[phrase1.phrase_id]
					var2 = variables[phrase2.phrase_id]

					expr = LinExpr()
					expr.addTerm(1.0, var1)
					expr.addTerm(1.0, var2)

					model.addConstr(expr, GRB.LESS_EQUAL, 1.0, 'i_within_i' + \
						phrase1.is_NP + ':' + phrase1.phrase_id + phrase2.phrase_id)

	def add_phrase_coocurrence_constraint(model, phrases, variables, linking_variables):
		for i in range(0, phrases - 1):
			phrase_i = phrases[i]
			var_i = variables[phrase_i.phrase_id]

			for j in range(i + 1, phrases):
				phrase_j = phrases[j]
				var_j = variables[phrase_j.phrase_id]
				key = self.build_key(phrase_i, phrase_j)
				var_ij = linking_variables[key]

				expr = LinExpr()
				expr.addTerms(1.0, var_ij)
				expr.addTerms(-1.0, var_i)
				model.addConstr(expr, GRB.LESS_EQUAL, 0.0, "phrase_coocurrence_1:" + phrase_i.isNP + key)

				expr = LinExpr()
				expr.addTerms(1.0, var_ij)
				expr.addTerms(-1.0, var_j)
				model.addConstr(expr, GRB.LESS_EQUAL, 0.0, "phrase_coocurrence_2:" + phrase_i.isNP + key)

				expr = LinExpr()
				expr.addTerms(1.0, var_i)
				expr.addTerms(1.0, var_j)
				expr.addTerms(-1.0, var_ij)
				model.addConstr(expr, GRB.LESS_EQUAL, 1.0, "phrase_coocurrence_3:" + phrase_i.isNP + key)
				
	def add_sentence_number_constraint(model, k):
		expr = LinExpr()

		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			expr.addTerm(1.0, var)

		model.addConstr(expr, GRB.LESS_EQUAL, k, "sentence_number")
	
	def add_short_sentence_avoidance_constraint(model, m):
		for vp in self.verb_phrases:
			if vp.sentence_length < m or vp.word_length < self.MINIMUM_VERB_LENGTH:
				var = self.verb_variables[vp.phrase_id]
				expr = LinExpr()
				expr.addTerms(1.0, var)

				model.addConstr(expr, GRB.EQUAL, 0.0, "short_sent_avoidance:" + vp.phrase_id)

	def add_pronoun_avoidance_constraint(model):
		for np in self.noun_phrases:
			if np.is_pronoun:
				var = self.noun_variables[np.phrase_id]
				expr = LinExpr()
				expr.addTerms(1.0, var)
				model.addConstr(expr, GRB.EQUAL, 0.0, "pronoun_avoidance:" + np.phrase_id)

	def add_length_constraint(model):
		expr = LinExpr()

		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			expr.addTerms(phrase.word_length, var)

		for vp in self.verb_phrases:
			var = verb_variables[vp.phrase_id]
			expr.addTerms(phrase.word_length, var)

		model.addConstr(expr, GRB.LESS_EQUAL, self.max_word_length, "length_constraint")

	def build_key(phrase1, phrase2):
		return phrase1.phrase_id + ':' + phrase2.phrase_id

	def find_optimal_solution(self):
		self.find_alt_VPs(self.noun_phrases, self.corefs.values())
		self.find_alt_VPs(self.verb_phrases)
		self.build_compatibility_matrix()
		return self.start_optimization()

	def update_model(self):
		self.noun_phrases = self.processor.noun_phrases
		self.verb_phrases = self.processor.verb_phrases
		self.all_phrases = self.processor.all_phrases
		self.corefs = self.processor.corefs
		self.nouns = self.processor.nouns
		self.verbs = self.processor.verbs
		self.docs = self.processor.docs

	def generate_summary(self):
		self.score_phrases()
		self.find_optimal_solution()


def main():
	parser = Parser()
	for dirpath, dirnames, filenames in os.walk(args.input_dir):
		for filename in filenames:
			if filename.startswith('.'):
				continue
			file_path = os.path.join(dirpath, filename)
			text = utility.load_file(file_path)
			parser.processDocument(text)

		parser.update_model()
		summary = parser.generate_summary()
		print(summary)

	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Abstractive Summarizer')
	parser.add_argument('input_dir', help='input folder containing all text files')
	parser.add_argument('out_file', help='output file')
	parser.add_argument('-w', '--word-length', help='maximum word length', default=DEFAULT_MAX_WORD_LENGTH)
	parser.add_argument('-v', '--vp-thresh', help='alternative VP threshold', default=DEFAULT_ALTERNATIVE_VP_THRESHOLD)
	parser.add_argument('-s', '--max-sent', help='maximum number of sentences', default=DEFAULT_MAXIMUM_SENTENCE)
	parser.add_argument('-t', '--threads', help='number of threads', default=0)
	parser.add_argument('-p', '--plaintext', help='is plain text data', default=False, action='store_true')
	parser.add_argument('-e', '--export-only', help='only export the phrases', default=False, action='store_true')
	args = parser.parse_args()

	main()