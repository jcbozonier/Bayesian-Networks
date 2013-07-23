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
			row[-1] = row[-1]/probability_sum
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
			row[-1] = row[-1]/probability_sum
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
			probability_shift = updated_probability / current_probability
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
	def update_applicable_beliefs(self, joint_probability_table):
		for event_name in joint_probability_table._columns:
			if event_name in self._columns:
				print "updating belief in " + event_name
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
	def affected_by(self, other_node):
		self._affected_by.append(other_node)
	def affects(self, node):
		self._affects_nodes.append(node)
		node.affected_by(self)
	def _forward_propagate(self, joint_probability_table):
		print "Forward propagating beliefs on " + str(self._name)
		print "Beliefs before: " + str(self._joint_probability_table)
		self._joint_probability_table.update_applicable_beliefs(joint_probability_table)
		print "Beliefs after: " + str(self._joint_probability_table)
		for affected_node in self._affects_nodes:
			affected_node._forward_propagate(self._joint_probability_table)
	def _backward_propagate(self, joint_probability_table):
		print "Backward propagating beliefs on " + str(self._name)
		print "With table: " +str(joint_probability_table)
		print "Beliefs before: " + str(self._joint_probability_table)
		self._joint_probability_table.update_applicable_beliefs(joint_probability_table)
		print "Beliefs after: " + str(self._joint_probability_table)
		for affected_node in self._affected_by:
			affected_node._backward_propagate(self._joint_probability_table)
	def given(self, value):
		self._joint_probability_table = self._joint_probability_table.given(self._name, value)
		jpt = self._joint_probability_table.clone()
		for affected_node in self._affects_nodes:
			affected_node._forward_propagate(jpt)
		for affected_node in self._affected_by:
			affected_node._backward_propagate(jpt)
	def probability(self, event_value):
		return self._joint_probability_table.probability(self._name)[event_value]
	def __str__(self):
		return str(self._joint_probability_table)

cloudy_table = JointProbabilityTable(
	columns=['cloudy'],
	data = [
		[True,  .5],
	 	[False, .5]
	 ])

sprinkler_table = JointProbabilityTable(
	columns=['sprinkler', 'cloudy'],
	data = [
		[True,  True,  .1],
		[True,  False, .5],
		[False, True,  .9],
		[False, False, .5],

	])

rain_table = JointProbabilityTable(
	columns=['rain', 'cloudy'],
	data = [
		[True,     True,      .8],
		[True,     False,     .2],
		[False,    True,      .2],
		[False,    False,     .8]
	])

wet_grass_table = JointProbabilityTable(
	columns=['sprinkler', 'rain', 'wet grass'],
	data = [
		[True, True,     True,      .99],
		[True, True,     False,     .01],
		[True, False,    True,      .90],
		[True, False,    False,     .10],
		[False, True,     True,     .9],
		[False, True,     False,    .1],
		[False, False,    True,      0],
		[False, False,    False,     1]
	])

print "Test given for wet grass event: " + str(wet_grass_table.given('wet grass', True))

wet_grass_node = BayesianNode('wet grass', wet_grass_table)
cloudy_node = BayesianNode('cloudy', cloudy_table)
rain_node = BayesianNode('rain', rain_table)
sprinkler_node = BayesianNode('sprinkler', sprinkler_table)

cloudy_node.affects(sprinkler_node)
cloudy_node.affects(rain_node)
sprinkler_node.affects(wet_grass_node)
rain_node.affects(wet_grass_node)

wet_grass_node.given(True)
print 'Sprinkler node: ' + str(sprinkler_node)
print 'P(S = True | W = True) = ' + str(sprinkler_node.probability(True))
print 'P(S = False | W = True) = ' + str(sprinkler_node.probability(False))
print 'P(R = True | W = True) = ' + str(rain_node.probability(True))
print 'P(C = True | W = True) = ' + str(cloudy_node.probability(True))



"""
print diner_order_probability.given('order', False)
adjusted_table = diner_order_probability.update_belief('diner loyalty', {'return': .3, 'new': .7})
print adjusted_table.update_belief('diner loyalty', {'return': .5, 'new': .5})

print "~~~~~~~~~~~ test smallest table"
print diner_loyalty_probability.update_belief('diner loyalty', {'return': .7, 'new': .3})



print "~~~~ Example Scenario ~~~~~~"
loyalty_probability_given_ordered = diner_order_probability.given('order', True)
loyalty_beliefs = loyalty_probability_given_ordered.probability('diner loyalty')
print "Given that an order was placed their loyalty probabilities are:"
print loyalty_beliefs
updated_channel_order_probability = channel_order_probability.update_belief('diner loyalty', loyalty_beliefs)
print "Given that an order was placed their channel probabilities are:"
print updated_channel_order_probability.probability('channel')
print "Given that the diner was new their channel probabilities are:"
print updated_channel_order_probability.given('diner loyalty', 'new')


order_node = BayesianNode('order', diner_order_probability)
channel_node = BayesianNode('channel', channel_order_probability)
loyalty_node = BayesianNode('diner loyalty', diner_loyalty_probability)

loyalty_node.affects(channel_node)
loyalty_node.affects(order_node)
channel_node.affects(order_node)

print 'Given that the diner ordered'
order_node.given(True)
print 'The probability they came from a direct channel is: ' + str(channel_node.probability('direct'))
print 'It should be 0.5483870967741936'


#channel_order_probability

#print "P(order) = " + str(diner_order_probability.probability('order'))
#loyalty_given_channel = channel_order_probability.given('channel', 'seo')
#new_beliefs = loyalty_given_channel.probability('diner loyalty')
#print new_beliefs
#conversion_by_loyalty_given_channel = diner_order_probability.update_belief('diner loyalty', new_beliefs)
#print conversion_by_loyalty_given_channel
#print conversion_by_loyalty_given_channel.probability('order')"""
