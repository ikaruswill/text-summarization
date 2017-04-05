import utility
from gurobi import *
from constraints import ConstraintAdder

class Optimizer():
	def __init__(self, parser):
		self.noun_phrases = parser.noun_phrases
		self.verb_phrases = parser.verb_phrases
		self.corefs = parser.corefs
		self.compatibility_matrix = parser.compatibility_matrix
		self.max_sentence = parser.max_sentence
		self.min_sentence_length = parser.min_sentence_length
		self.min_verb_length = parser.min_verb_length
		self.max_word_length = parser.max_word_length

		self.model = Model()
		self.model.Params.Threads = parser.threads
		objective = LinExpr()

		self._init_variables(objective)
		self._init_linking_variables(objective)
		self.model.update()
		self.model.setObjective(objective, GRB.MAXIMIZE)

		self._init_constraints()

	def _init_variables(self, expr):
		self.noun_variables = {}
		self.verb_variables = {}
		self.gamma_variables = {}

		for np in self.noun_phrases:
			var = self.model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "n:" + str(np.phrase_id))
			self.noun_variables[np.phrase_id] = var
			expr.addTerms(np.score, var)

			for vp in self.verb_phrases:
				if self.compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + utility.build_key(np, vp)
					gamma = self.model.addVar(0.0, 1.0, 1.0, GRB.BINARY, key)
					self.gamma_variables[key] = gamma

		for vp in self.verb_phrases:
			var = self.model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "v:" + str(vp.phrase_id))
			self.verb_variables[vp.phrase_id] = var
			expr.addTerms(vp.score, var)

	def _init_linking_variables(self, expr):
		self.noun_to_noun_variables = {}
		self.verb_to_verb_variables = {}

		len_noun_phrases = len(self.noun_phrases)
		for i in range(0, len_noun_phrases - 1):
			for j in range(i + 1, len_noun_phrases):
				np1 = self.noun_phrases[i]
				np2 = self.noun_phrases[j]
				key = utility.build_key(np1, np2)

				var = self.model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "n2n:" + key)
				self.noun_to_noun_variables[key] = var
				score = -(np1.score + np2.score) * self.calculate_similarity(np1, np2)
				expr.addTerms(score, var)

		len_verb_phrases = len(self.verb_phrases)
		for i in range(0, len_verb_phrases - 1):
			for j in range(i + 1, len_verb_phrases):
				vp1 = self.verb_phrases[i]
				vp2 = self.verb_phrases[j]
				key = utility.build_key(vp1, vp2)

				var = self.model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "v2v:" + key)
				self.verb_to_verb_variables[key] = var
				score = -(vp1.score + vp2.score) * self.calculate_similarity(vp1, vp2)
				expr.addTerms(score, var)

	def _init_constraints(self):
		ca = ConstraintAdder(self)
		ca.NP_validity()
		ca.VP_validity()
		ca.NP_not_i_within_i()
		ca.VP_not_i_within_i()
		ca.NP_co_occurrence()
		ca.VP_co_occurrence()
		ca.sentence_number(self.max_sentence)
		ca.short_sentence_avoidance(self.min_sentence_length, self.min_verb_length)
		ca.pronoun_avoidance()
		ca.word_length(self.max_word_length)

	def calculate_similarity(self, phrase1, phrase2):
		for coref_set in self.corefs.values():
			if phrase1.content in coref_set and phrase2.content in coref_set:
				return 1.0

		return utility.calculate_jaccard_index(phrase1, phrase2)

	def optimize(self):
		self.model.optimize()

	def generate_summary(self):
		selected_nouns = {}
		selected_verbs = {}

		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			selected = var.X

			if selected > 0:
				selected_nouns[np.phrase_id] = np

		for vp in self.verb_phrases:
			var = self.verb_variables[vp.phrase_id]
			selected = var.X

			if selected > 0:
				selected_verbs[vp.phrase_id] = np

		selected_NP_lists = {}
		summary_sentences = {} # SortedDict

		for key, var in self.gamma_variables.items():
			value = var.X

			if value > 0:
				data = key.split(':')
				noun_id = int(data[1])
				verb_id = int(data[2])

				if not noun_id in selected_NP_lists:
					selected_NP_lists[noun_id] = []

				selected_NP_lists[noun_id].append(selected_verbs[verb_id])

		summary = ""

		for key, np_list in selected_NP_lists.items():
			np = selected_nouns[key]
			phrases = selected_NP_lists[key]
			sentence = np.content + " "
			min_id = sys.maxsize

			verbs = []
			phrases.sort(key=operator.attrgetter('phrase_id'))

			for phrase in phrases:
				if not phrase.is_NP and min_id > phrase.phrase_id:
					mind_id = phrase.phrase_id
				verbs.append(phrase.content)

			sentence += ', '.join(verbs)
			summary_sentences[min_id] = sentence

		for key, sentence in sorted(summary_sentences.items()):
			summary += sentence + '\n'

		return summary