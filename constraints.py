from gurobi import *
import utility

class ConstraintAdder():
	def __init__(self, optimizer):
		self.model = optimizer.model
		self.noun_phrases = optimizer.noun_phrases
		self.verb_phrases = optimizer.verb_phrases
		self.noun_variables = optimizer.noun_variables
		self.verb_variables = optimizer.verb_variables
		self.gamma_variables = optimizer.gamma_variables
		self.noun_to_noun_variables = optimizer.noun_to_noun_variables
		self.verb_to_verb_variables = optimizer.verb_to_verb_variables
		self.compatibility_matrix = optimizer.compatibility_matrix

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

					self.model.addConstr(expr, GRB.GREATER_EQUAL, 0.0, label + ':' + str(np.phrase_id))

					constraint.addTerms(1.0, var)

			constraint.addTerms(-1.0, np_var)
			self.model.addConstr(constraint, GRB.GREATER_EQUAL, 0.0, label + ':' + str(np.phrase_id))

	def VP_validity(self):
		label = 'vp_validity'
		for vp in self.verb_phrases:
			vp_var = self.verb_variables[vp.phrase_id]
			constraint = LinExpr()
			constraint.addTerms(-1.0, vp_var)

			for np in self.noun_phrases:
				if self.compatibility_matrix[(np, vp)] == 1:
					key = 'gamma:' + utility.build_key(np, vp)
					var = self.gamma_variables[key]

					constraint.addTerms(1.0, var)

			self.model.addConstr(constraint, GRB.EQUAL, 0.0, label + ':' + str(vp.phrase_id))

	def NP_not_i_within_i(self):
		self._not_i_within_i(self.noun_phrases, self.noun_variables)

	def VP_not_i_within_i(self):
		self._not_i_within_i(self.verb_phrases, self.verb_variables)

	def _not_i_within_i(self, phrases, variables):
		label = 'i_within_i'
		len_phrases = len(phrases)
		for i in range(0, len_phrases - 1):
			for j in range(i + 1, len_phrases):
				phrase1 = phrases[i]
				phrase2 = phrases[j]
				if phrase1.phrase_id == phrase2.parent_id:
					var1 = variables[phrase1.phrase_id]
					var2 = variables[phrase2.phrase_id]

					expr = LinExpr()
					expr.addTerms(1.0, var1)
					expr.addTerms(1.0, var2)

					self.model.addConstr(expr, GRB.LESS_EQUAL, 1.0, label + ':' + \
						str(phrase1.is_NP) + ':' + str(phrase1.phrase_id) + ':' + str(phrase2.phrase_id))

	def NP_co_occurrence(self):
		self._co_occurrence(self.noun_phrases, self.noun_variables, self.noun_to_noun_variables)

	def VP_co_occurrence(self):
		self._co_occurrence(self.verb_phrases, self.verb_variables, self.verb_to_verb_variables)

	def _co_occurrence(self, phrases, variables, linking_variables):
		label = 'phrase_co_occurrence'
		len_phrases = len(phrases)
		for i in range(0, len_phrases - 1):
			phrase_i = phrases[i]
			var_i = variables[phrase_i.phrase_id]

			for j in range(i + 1, len_phrases):
				phrase_j = phrases[j]
				var_j = variables[phrase_j.phrase_id]
				key = utility.build_key(phrase_i, phrase_j)
				var_ij = linking_variables[key]

				expr = LinExpr()
				expr.addTerms(1.0, var_ij)
				expr.addTerms(-1.0, var_i)
				self.model.addConstr(expr, GRB.LESS_EQUAL, 0.0, label + '_1:' + str(phrase_i.is_NP) + key)

				expr = LinExpr()
				expr.addTerms(1.0, var_ij)
				expr.addTerms(-1.0, var_j)
				self.model.addConstr(expr, GRB.LESS_EQUAL, 0.0, label + '_2:' + str(phrase_i.is_NP) + key)

				expr = LinExpr()
				expr.addTerms(1.0, var_i)
				expr.addTerms(1.0, var_j)
				expr.addTerms(-1.0, var_ij)
				self.model.addConstr(expr, GRB.LESS_EQUAL, 1.0, label + '_3:' + str(phrase_i.is_NP) + key)
				
	def sentence_number(self, k):
		label = 'sentence_number'
		expr = LinExpr()

		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			expr.addTerms(1.0, var)

		self.model.addConstr(expr, GRB.LESS_EQUAL, k, label)

	def short_sentence_avoidance(self, min_sentence_length, min_verb_length):
		label = 'short_sent_avoidance'
		for vp in self.verb_phrases:
			if vp.sentence_length < min_sentence_length or vp.word_length < min_verb_length:
				var = self.verb_variables[vp.phrase_id]
				expr = LinExpr()
				expr.addTerms(1.0, var)

				self.model.addConstr(expr, GRB.EQUAL, 0.0, label + ':' + str(vp.phrase_id))

	def pronoun_avoidance(self):
		label = 'pronoun_avoidance'
		for np in self.noun_phrases:
			if np.is_pronoun:
				var = self.noun_variables[np.phrase_id]
				expr = LinExpr()
				expr.addTerms(1.0, var)
				self.model.addConstr(expr, GRB.EQUAL, 0.0, label + ':' + str(np.phrase_id))

	def word_length(self, max_word_length):
		label = 'length_constraint'
		expr = LinExpr()
		for np in self.noun_phrases:
			var = self.noun_variables[np.phrase_id]
			expr.addTerms(np.word_length, var)

		for vp in self.verb_phrases:
			var = self.verb_variables[vp.phrase_id]
			expr.addTerms(vp.word_length, var)

		self.model.addConstr(expr, GRB.LESS_EQUAL, max_word_length, label)