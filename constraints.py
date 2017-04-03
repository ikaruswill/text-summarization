from gurobi import *
import utility

class ConstraintAdder():
	def __init__(self, model, noun_phrases, verb_phrases, noun_variables, verb_variables, gamma_variables, compatibility_matrix):
		self.model = model
		self.noun_phrases = noun_phrases
		self.verb_phrases = verb_phrases
		self.noun_variables = noun_variables
		self.verb_variables = verb_variables
		self.gamma_variables = gamma_variables
		self.compatibility_matrix = compatibility_matrix

	def NP_validity(self):
		label = 'np_validity'
		for np in self.noun_phrases:
			np_var = self.noun_variables[np.phrase_id]
			constraint = LinExpr()

			for vp in self.verb_phrases:
				if self.compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + utility.build_key(np, vp)
					var = self.gamma_variables[key]

					expr = LinExpr()
					expr.addTerms(1.0, np_var)
					expr.addTerms(-1.0, var)

					self.model.addConstr(expr, GRB.GREATER_EQUAL, 0.0, label + ':' + noun.phrase_id)

					constraint.addTerms(1.0, var)

			constraint.addTerms(-1.0, np_var)
			self.model.addConstr(constraint, GRB.GREATER_EQUAL, 0.0, label + ':' + noun.phrase_id)

	def VP_validity(self):
		label = 'vp_validity'
		for vp in self.verb_phrases:
			vp_var = self.verb_variables[vp.phrase_id]
			constraint = LinExpr()
			contraint.addTerms(-1.0, vp_var)

			for np in self.noun_phrases:
				if self.compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + utility.build_key(np, vp)
					var = self.gamma_variables[key]

					contraint.addTerms(1.0, var)

			self.model.addConstr(constr, GRB.EQUAL, 0.0, label + ':' + vp.phrase_id)

	def _not_i_within_i(self, phrases, variables):
		label = 'i_within_i'
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

					self.model.addConstr(expr, GRB.LESS_EQUAL, 1.0, label + ':' + \
						phrase1.is_NP + ':' + phrase1.phrase_id + phrase2.phrase_id)

	def _phrase_coocurrence(self, phrases, variables, linking_variables):
		label = 'phrase_coocurrence'
		for i in range(0, phrases - 1):
			phrase_i = phrases[i]
			var_i = variables[phrase_i.phrase_id]

			for j in range(i + 1, phrases):
				phrase_j = phrases[j]
				var_j = variables[phrase_j.phrase_id]
				key = utility.build_key(phrase_i, phrase_j)
				var_ij = linking_variables[key]

				expr = LinExpr()
				expr.addTerms(1.0, var_ij)
				expr.addTerms(-1.0, var_i)
				self.model.addConstr(expr, GRB.LESS_EQUAL, 0.0, label + '_1:' + phrase_i.isNP + key)

				expr = LinExpr()
				expr.addTerms(1.0, var_ij)
				expr.addTerms(-1.0, var_j)
				self.model.addConstr(expr, GRB.LESS_EQUAL, 0.0, label + '_2:' + phrase_i.isNP + key)

				expr = LinExpr()
				expr.addTerms(1.0, var_i)
				expr.addTerms(1.0, var_j)
				expr.addTerms(-1.0, var_ij)
				self.model.addConstr(expr, GRB.LESS_EQUAL, 1.0, label + '_3:' + phrase_i.isNP + key)
				
	def sentence_number(self, k):
		label = 'sentence_number'
		expr = LinExpr()

		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			expr.addTerm(1.0, var)

		self.model.addConstr(expr, GRB.LESS_EQUAL, k, label)

	def short_sentence_avoidance(self, min_sentence_length, min_verb_length):
		label = 'short_sent_avoidance'
		for vp in self.verb_phrases:
			if vp.sentence_length < min_sentence_length or vp.word_length < min_verb_length:
				var = self.verb_variables[vp.phrase_id]
				expr = LinExpr()
				expr.addTerms(1.0, var)

				self.model.addConstr(expr, GRB.EQUAL, 0.0, label + ':' + vp.phrase_id)

	def pronoun_avoidance(self):
		label = 'pronoun_avoidance'
		for np in self.noun_phrases:
			if np.is_pronoun:
				var = self.noun_variables[np.phrase_id]
				expr = LinExpr()
				expr.addTerms(1.0, var)
				self.model.addConstr(expr, GRB.EQUAL, 0.0, label + ':' + np.phrase_id)

	def length(self, max_word_length):
		label = 'length_constraint'
		expr = LinExpr()
		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			expr.addTerms(np.word_length, var)

		for vp in self.verb_phrases:
			var = self.verb_variables[vp.phrase_id]
			expr.addTerms(vp.word_length, var)

		self.model.addConstr(expr, GRB.LESS_EQUAL, max_word_length, label)