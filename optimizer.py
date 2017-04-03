import utility
from gurobi import *

class Optimizer():
	def __init__(self, noun_phrases, verb_phrases, threads):
		self.threads = threads
		self.noun_phrases = noun_phrases
		self.verb_phrases = verb_phrases

		self.noun_variables = {}
		self.verb_variables = {}
		self.gamma_variables = {}

		self.noun_to_noun_variables = {}
		self.verb_to_verb_variables = {}

	def calculate_similarity(self, phrase1, phrase2):
		for coref_set in self.corefs.values():
			if a.content in coref_set and b.content in coref_set:
				return 1.0

		return utility.calculate_jaccard_index(phrase1, phrase2)

	def start_optimization(self):
		env = Env()
		env.Params.Threads = self.threads
		model = Model(env=env)

		expr = LinExpr()

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