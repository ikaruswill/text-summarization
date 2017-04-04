import utility
from units import InputDocument, Phrase

class PhraseExtractor():
	def __init__(self, input_document, indicator_matrix):
		self.input_document = input_document
		self.indicator_matrix = indicator_matrix

	def extract_all_phrases(self):
		all_phrases = []
		sentences = self.input_document.sentences

		for i, sentence in enumerate(sentences):
			phrases_in_sentence = self.extract_phrases(self.input_document.parse_trees[i], utility.count_words(sentence))

			all_phrases.extend(phrases_in_sentence)
			len_phrases_in_sentence = len(phrases_in_sentence)
			for i in range(0, len_phrases_in_sentence - 1):
				for j in range(i + 1, len_phrases_in_sentence):
					a = phrases_in_sentence[i]
					b = phrases_in_sentence[j]
					if a.is_NP and not b.is_NP and a.sentence_node_id == b.sentence_node_id:
						self.indicator_matrix[(a,b)] = 1
		return all_phrases
		
	def extract_phrases(self, parse_tree, sentence_length):
		phrases = []

		s_length = 0
		sentence_node_id = 0
		l1_npvps = []

		nodes = parse_tree.split('\n')
		# Ignore ROOT node, get children of top most S node
		for i, node in enumerate(nodes):
			# Iterate only level 1 nodes
			if node.startswith('    ('):
				node = node.strip()
				# Ignore irrelevant nodes
				if not node.startswith('(NP') and not node.startswith('(VP') \
				and not node.startswith('(S') and not node.startswith('(SBAR'):
					continue

				# Create new phrase
				is_not_VP = not node.startswith('(VP')
				phrase_content = self.get_phrase_text(nodes, i)
				phrase = Phrase(phrase_content, is_not_VP, -1, 0)
				phrase.concepts = self.input_document.extract_concepts_from_string(phrase_content)
				# Set current phrase sentence length to root sentence length
				phrase.sentence_length = sentence_length
				phrases.append(phrase)

				# NP or VP
				if node.startswith('(NP') or node.startswith('(VP'):
					# Calculate l1 sentence length excluding irrelevant elements
					s_length += phrase.word_length
					l1_npvps.append(phrase)
				# S or SBAR
				else:
					# Set sentence length to current S node length
					sentence_length = phrase.word_length
					sentence_node_id += 1

				is_VP = not is_not_VP

				if is_VP:
					first_child = nodes[i + 1].strip()
					# Stop further processing if first child is MD, VBZ, VBP or VBD
					if first_child.startswith('MD') or first_child.startswith('VBZ') \
					or first_child.startswith('VBP') or first_child.startswith('VBD'):
						continue

					sub_VP_count = 0
					for child in nodes[i + 1:]:
						# If current node is no longer part of the subtree, stop
						if not child.startswith('      '):
							break

						# If current node is a child of the direct child, skip
						if not child.startswith('      ('):
							continue

						# If is child of current node and is VP
						if child.strip().startswith('(VP'):
							sub_VP_count += 1
						
					# Stop further processing if less than 2 sub VPs
					if sub_VP_count < 2: 
						continue

				for child in nodes[i + 1:]:
					# If current node is no longer part of the subtree, stop
					if not child.startswith('      '):
						break

					# If current node is a child of the direct child, skip
					if not child.startswith('      ('):
						continue

					# If l2 node is NP and l1 node is S, SBAR or NP
					# If l2 node is VP and l1 node is VP
					if is_not_VP and child.strip().startswith('(NP') \
					or is_VP and child.strip().startswith('(VP'):
						subphrase_content = self.get_phrase_text(nodes, i)
						subphrase = Phrase(subphrase_content, is_not_VP, phrase.phrase_id, sentence_node_id)
						subphrase.concepts = self.input_document.extract_concepts_from_string(subphrase_content)
						# Set subphrase sentence_length to parent S node length
						subphrase.sentence_length = sentence_length
						phrases.append(subphrase)
		
		# Set l1 NPs and VPs to l1 sentence length excluding ignored elements
		for l1_npvp in l1_npvps:
			l1_npvp.sentence_length = s_length

		return phrases

	def get_phrase_text(self, nodes, index):
		parent_indentation = nodes[index][:nodes[index].find('(')]
		child_indentation = parent_indentation + '  '
		
		# Extract from target
		phrase_text = self.extract_node_text(nodes[index])

		# Extract from children
		for child in nodes[index + 1:]:
			# If current node is no longer part of the subtree, stop
			if not child.startswith(child_indentation):
				break

			node_text = self.extract_node_text(child)
			if node_text != '':
				phrase_text += ' ' + node_text

		return phrase_text

	def extract_node_text(self, node):
		text = ''
		node = node.strip()
		node_contents = node.split(' (')
		if len(node_contents) < 2:
			# Single node
			if node.endswith(')'):
				text = self._strip_brackets(node)
				text = text.split()[-1]
				return text
			# Parent node
			return text

		for unit in node_contents[1:]:
			unit = self._strip_brackets(unit)
			text += ' ' + unit.split()[-1]
		return text.strip()

	def get_first_child_type(self, nodes, index):
		node = nodes[index].strip()
		# Has children in node or is leaf
		if node.endswith(')'):
			node_contents = node.split(' (')
			# No children
			if len(node_contents) < 2:
				return
			# Children in node
			else:
				first_child = node_contents[1]
				# Brackets already removed by split
				return first_child.split()[0]
		# Children in next node in list
		else:
			first_child = nodes[i + 1].strip()
			return self._strip_brackets(first_child).split()[0]

	def _strip_brackets(self, text):
		while text.startswith('('):
			text = text.lstrip('(')
		while text.endswith(')'):
			text = text.rstrip(')')
		return text
