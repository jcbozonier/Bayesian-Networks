class JointProbabilityTable:
	def __init__(self, columns, data):
		self._columns = columns
		self._probability_index = len(columns)
		self._data = self._normalize(data)
	def _normalize(self, data):
		probability_sum = 0
		for row in data:
			probability_sum += row[-1]
		for row in data:
			if probability_sum != 0:
				row[-1] = row[-1]/probability_sum
			else:
				row[-1] = 0
		return data
	def given(self, event_name, event_happened_value):
		contextual_columns = [entry for entry in self._columns]
		contextual_data = []
		event_column_index = self._columns.index(event_name)
		probability_sum = 0
		for row in self._data:
			if row[event_column_index] == event_happened_value:
				new_row = [entry for i, entry in enumerate(row)]
				probability_sum += new_row[-1]
				contextual_data.append(new_row)
			else:
				new_row = [entry for i, entry in enumerate(row)]
				new_row[-1] = 0
				contextual_data.append(new_row)
		for row in contextual_data:
			if probability_sum != 0:
				row[-1] = row[-1]/probability_sum
			else:
				row[-1] = 0
		return JointProbabilityTable(contextual_columns, contextual_data)
	def _add_to_current_beliefs(self, current_beliefs, event_value, probability):
		if not event_value in current_beliefs:
			current_beliefs[event_value] = 0
		current_beliefs[event_value] += probability
	def _get_matching_probability(self, new_beliefs, event_value):
		for new_belief in new_beliefs:
			if new_belief[0] == event_value:
				return new_belief[1]
	def _clone_data(self):
		return [list(row) for row in self._data]
	def update_belief(self, event_name, new_beliefs):
		current_beliefs = {}
		belief_shifts = {}
		event_column_index = self._columns.index(event_name)
		for row in self._data:
			self._add_to_current_beliefs(current_beliefs, row[event_column_index], row[self._probability_index])
		for event_value in new_beliefs:
			updated_probability = new_beliefs[event_value]
			current_probability = current_beliefs[event_value]
			if current_probability != 0:
				probability_shift = updated_probability / current_probability
			else:
				probability_shift = 0
			belief_shifts[event_value] = probability_shift
		new_table = self._clone_data()
		for row in new_table:
			row[-1] = row[-1] * belief_shifts[row[event_column_index]]
		return JointProbabilityTable(self._columns, new_table)
	def probability(self, event_name):
		beliefs = {}
		event_column_index = self._columns.index(event_name)
		for row in self._data:
			event_value = row[event_column_index]
			if not (event_value in beliefs):
				beliefs[event_value] = 0
			beliefs[event_value] += row[-1]
		return beliefs
	def update_applicable_beliefs(self, node_name, joint_probability_table):
		for event_name in joint_probability_table._columns:
			if event_name in self._columns:
				event_beliefs = joint_probability_table.probability(event_name)
				self._data = self.update_belief(event_name, event_beliefs)._data
	def clone(self):
		return JointProbabilityTable(self._columns, self._clone_data())
	def __str__(self):
		return str([self._columns, self._data])

class BayesianNode:
	def __init__(self, name, joint_probability_table):
		self._name = name
		self._original_joint_probability_table = joint_probability_table
		self._joint_probability_table = joint_probability_table
		self._affects_nodes = []
		self._affected_by = []
		self._known = False
	def affected_by(self, other_node):
		self._affected_by.append(other_node)
	def affects(self, node):
		self._affects_nodes.append(node)
		node.affected_by(self)
	def _forward_propagate(self, joint_probability_table):
		self._joint_probability_table.update_applicable_beliefs(self._name, joint_probability_table)
		for affected_node in self._affects_nodes:
			affected_node._forward_propagate(self._joint_probability_table)
	def _backward_propagate(self, joint_probability_table):
		self._joint_probability_table.update_applicable_beliefs(self._name, joint_probability_table)
		for affected_node in self._affected_by:
			affected_node._backward_propagate(self._joint_probability_table)
	def given(self, value):
		if not self._known:
			self._joint_probability_table = self._joint_probability_table.given(self._name, value)
			self._known = True
			jpt = self._joint_probability_table.clone()
			for affected_node in self._affects_nodes:
				affected_node._forward_propagate(jpt)
			for affected_node in self._affected_by:
				affected_node._backward_propagate(jpt)
			for affected_node in self._affects_nodes:
				affected_node._backward_propagate(jpt)
			for affected_node in self._affected_by:
				affected_node._forward_propagate(jpt)
	def probability(self):
		return self._joint_probability_table.probability(self._name)
	def __str__(self):
		return str(self._joint_probability_table)

door_picked_table = JointProbabilityTable(
	columns=['door_picked'],
	data = [
		['red',   0.3333],
		['blue',  0.3333],
		['green', 0.3334],

	])

prize_behind_door_table = JointProbabilityTable(
	columns=['prize_behind'],
	data = [
		['red',   0.3333],
		['blue',  0.3333],
		['green', 0.3334],
	])

shown_empty_table = JointProbabilityTable(
	columns=['door_picked', 'prize_behind', 'shown_empty'],
	data = [
		['red', 'red',  'red',       0.0],
		['red', 'red',  'green',     0.5],
		['red', 'red',  'blue',      0.5],
		['red', 'green',  'red',     0.0],
		['red', 'green',  'green',   0.0],
		['red', 'green',  'blue',    1.0],
		['red', 'blue',  'red',      0.0],
		['red', 'blue',  'green',    1.0],
		['red', 'blue',  'blue',     0.0],

		['green', 'red',  'red',     0.0],
		['green', 'red',  'green',   0.0],
		['green', 'red',  'blue',    1.0],
		['green', 'green',  'red',   0.5],
		['green', 'green',  'green', 0.0],
		['green', 'green',  'blue',  0.5],
		['green', 'blue',  'red',    1.0],
		['green', 'blue',  'green',  0.0],
		['green', 'blue',  'blue',   0.0],

		['blue', 'red',  'red',      0.0],
		['blue', 'red',  'green',    1.0],
		['blue', 'red',  'blue',     0.0],
		['blue', 'green',  'red',    1.0],
		['blue', 'green',  'green',  0.0],
		['blue', 'green',  'blue',   0.0],
		['blue', 'blue',  'red',     0.5],
		['blue', 'blue',  'green',   0.5],
		['blue', 'blue',  'blue',    0.0],
	])

switch_table = JointProbabilityTable(
	columns=['switch_or_stay'],
	data=[
		['switch',  0.5],
		['stay', 0.5],
	])

door_after_choice_table = JointProbabilityTable(
	columns=['door_picked', 'shown_empty', 'switch_or_stay', 'door_after_choice'],
	data=[
		['red', 'red', 'switch', 'red',    0.0],
		['red', 'red', 'switch', 'green',  0.0],
		['red', 'red', 'switch', 'blue',   0.0],
		['red', 'red', 'stay', 'red',      0.0],
		['red', 'red', 'stay', 'green',    0.0],
		['red', 'red', 'stay', 'blue',     0.0],

		['red', 'blue', 'switch', 'red',   0.0],
		['red', 'blue', 'switch', 'blue',  0.0],
		['red', 'blue', 'switch', 'green', 1.0],
		['red', 'blue', 'stay', 'red',     1.0],
		['red', 'blue', 'stay', 'blue',    0.0],
		['red', 'blue', 'stay', 'green',   0.0],

		['red', 'green', 'switch', 'red',   0.0],
		['red', 'green', 'switch', 'blue',  1.0],
		['red', 'green', 'switch', 'green', 0.0],
		['red', 'green', 'stay', 'red',     1.0],
		['red', 'green', 'stay', 'blue',    0.0],
		['red', 'green', 'stay', 'green',   0.0],

		#~~~~~~~~

		['blue', 'red', 'switch', 'red',    0.0],
		['blue', 'red', 'switch', 'green',  1.0],
		['blue', 'red', 'switch', 'blue',   0.0],
		['blue', 'red', 'stay', 'red',      0.0],
		['blue', 'red', 'stay', 'green',    0.0],
		['blue', 'red', 'stay', 'blue',     1.0],

		['blue', 'blue', 'switch', 'red',   0.0],
		['blue', 'blue', 'switch', 'blue',  0.0],
		['blue', 'blue', 'switch', 'green', 0.0],
		['blue', 'blue', 'stay', 'red',     0.0],
		['blue', 'blue', 'stay', 'blue',    0.0],
		['blue', 'blue', 'stay', 'green',   0.0],

		['blue', 'green', 'switch', 'red',   1.0],
		['blue', 'green', 'switch', 'blue',  0.0],
		['blue', 'green', 'switch', 'green', 0.0],
		['blue', 'green', 'stay', 'red',     0.0],
		['blue', 'green', 'stay', 'blue',    0.0],
		['blue', 'green', 'stay', 'green',   1.0],

		#~~~~~~~~

		['green', 'red', 'switch', 'red',    0.0],
		['green', 'red', 'switch', 'green',  0.0],
		['green', 'red', 'switch', 'blue',   1.0],
		['green', 'red', 'stay', 'red',      0.0],
		['green', 'red', 'stay', 'green',    1.0],
		['green', 'red', 'stay', 'blue',     0.0],

		['green', 'blue', 'switch', 'red',   1.0],
		['green', 'blue', 'switch', 'blue',  0.0],
		['green', 'blue', 'switch', 'green', 0.0],
		['green', 'blue', 'stay', 'red',     0.0],
		['green', 'blue', 'stay', 'blue',    1.0],
		['green', 'blue', 'stay', 'green',   0.0],

		['green', 'green', 'switch', 'red',   0.0],
		['green', 'green', 'switch', 'blue',  0.0],
		['green', 'green', 'switch', 'green', 0.0],
		['green', 'green', 'stay', 'red',     0.0],
		['green', 'green', 'stay', 'blue',    0.0],
		['green', 'green', 'stay', 'green',   0.0],
		
	])

win_prize_table = JointProbabilityTable(
	columns=['prize_behind', 'door_after_choice', 'win_prize'],
	data = [
		['red', 'red',    True,  1.0],
		['red', 'red',    False, 0.0],
		['red', 'green',  True,  0.0],
		['red', 'green',  False, 1.0],
		['red', 'blue',   True,  0.0],
		['red', 'blue',   False, 1.0],

		['green', 'red',  True,  0.0],
		['green', 'red',  False, 1.0],
		['green', 'green',True,  1.0],
		['green', 'green',False, 0.0],
		['green', 'blue', True,  0.0],
		['green', 'blue', False, 1.0],

		['blue', 'red',   True,  0.0],
		['blue', 'red',   False, 1.0],
		['blue', 'green', True,  0.0],
		['blue', 'green', False, 1.0],
		['blue', 'blue',  True,  1.0],
		['blue', 'blue',  False, 0.0],
	])

door_picked_node = BayesianNode('door_picked', door_picked_table)
prize_behind_node = BayesianNode('prize_behind', prize_behind_door_table)
shown_empty_node = BayesianNode('shown_empty', shown_empty_table)
win_prize_node = BayesianNode('win_prize', win_prize_table)
door_after_choice_node = BayesianNode('door_after_choice', door_after_choice_table)
switch_node = BayesianNode('switch_or_stay', switch_table)

print "Win prize original: " + str(win_prize_table.probability('win_prize'))

# Original
door_picked_node.affects(shown_empty_node)
prize_behind_node.affects(shown_empty_node)

# New
shown_empty_node.affects(door_after_choice_node)
door_picked_node.affects(door_after_choice_node)
door_after_choice_node.affects(win_prize_node)

prize_behind_node.affects(win_prize_node)
switch_node.affects(door_after_choice_node)

def print_all_nodes():
	print ""
	print "Door picked: " + str(door_picked_node.probability())
	print "Prize behind door: " + str(prize_behind_node.probability())
	print "Door shown empty: " + str(shown_empty_node.probability())
	print "Win prize: " + str(win_prize_node.probability())
	print "Updated door choice: " + str(door_after_choice_node.probability())
	print "Switch or stay: " + str(switch_node.probability())
	print "~~~~~"

print "Before doing anything..."
print_all_nodes()

door_picked_node.given('red')
print "After initially picking the red door..."
print_all_nodes()

shown_empty_node.given('green')
print "After being shown the green door..."
print_all_nodes()

switch_node.given('switch')
print "After switching doors..."
print_all_nodes()

print "After choosing another color door..."
door_after_choice_node.given('blue')
print_all_nodes()