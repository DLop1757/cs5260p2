import random
import numpy as np
from itertools import chain, combinations


class State(tuple):
	# A state is defined as a tuple (numbers, dice_summation)
	# Access with the following command:
	# numbers, dice_summation = state
	def __new__(self, numbers_left, dice_summation):
		return tuple.__new__(State, (frozenset(numbers_left), dice_summation))

class Environment:
	def __all_states_and_actions(self):
		all_numbers_left = [[], [1]]
		for i in range(2, self.total_numbers + 1):
			for curr in range(len(all_numbers_left)):
				curr_ = all_numbers_left[curr].copy()
				curr_.append(i)
				all_numbers_left.append(curr_)

		all_dice_summation = list(range(2, 12 + 1))

		states = []
		actions = {}
		
		for number_list in all_numbers_left:
			for dice in all_dice_summation:
				states.append(State(number_list, dice))
				actions[State(number_list, dice)] = []

		for numbers in all_numbers_left:
			all_combinations = chain.from_iterable(combinations(numbers, r) for r in range(len(numbers)+1))
			for combination in all_combinations:
				dice = self.calc_sum(combination)
				if dice>=2 and dice<=12:
					actions[State(numbers, dice)].append(combination)
		
		return states, actions


	def __init__(self):
		self.total_numbers = 9
		self.prob_dist = {i:0 for i in range(2, 12 + 1)}
		for i in range(1, 6 + 1):
			for j in range(1, 6 + 1):
				self.prob_dist[i+j] += 1/6 * 1/6
		self.all_states, self.all_states_actions = self.__all_states_and_actions()

	def available_actions(self, state):
		# Return a list of actions that is allowed in this case
		# Each action is a set of numbers.
		return self.all_states_actions[state]

	def all_transition_next(self, numbers_left, action_taken):
		# Return a list of all possible next steps with their probability.
		# Input: Current numbers and an action (a subset of previous numbers)
		# Each next step is represented in tuple (state, probability of the state)
		# State is a tuple itself - (numbers_left, dice_summation) 
		numbers_left = set(numbers_left)
		for it in action_taken:
			numbers_left.remove(it)
		return [(State(numbers_left, sum_), self.prob_dist[sum_]) for sum_ in self.prob_dist]

	def get_all_states(self):
		# Get a list of all states
		# Each state is a tuple - (numbers_left, dice_summation) 
		return self.all_states

	def calc_sum(self, numbers):
		# Calculate the summation of things in a list/set
		s = 0
		for i in numbers:
			s += i
		return s

class Agent:
	def __init__(self, env):
		self.env = env
		self.all_states = env.get_all_states()
		self.utilities = {state:0 for state in self.all_states}

	def giveup_reward(self, numbers_left):
		# The reward for choosing give up at this state
		c = self.env.total_numbers
		return c*(c+1)//2 - self.env.calc_sum(numbers_left)

	# returns utility
	def value_iteration(self):
		delta = 1e5
		# utility function array init to 0
		V = np.zeros(len(self.all_states))
		# do we use this?
		discount_factor = 1.0
		while delta >= 0.001:
			V_ = V.copy() # Copy the utility
			delta = 0 # Measure the maximum change in all states for this iteration - if smaller than 0.001 we stop.
			# iterate through states
			for s in range(len(self.all_states)):	
				# keep track of action utilities
				A = np.zeros(len(self.env.available_actions(self.all_states[s])))
				# reward
				rew = self.giveup_reward(self.all_states[s][0])
				# iterate through all actions
				for a in range(len(A)):
					# if no actions, skip and go directly to reward
					if (len(A) == 1):
						break
					# calc probability of next actions
					prob = self.env.all_transition_next(self.all_states[s][0], self.env.available_actions(self.all_states[s])[a])[a-1][1]
					# calculate utility for each action
					A[a] += prob * (rew + discount_factor * V_[s])
				# if there are no actions, skip the np.max function and just use reward
				try:
					best_action_val = np.max(A)
				except ValueError:
					best_action_val = rew
				# calc delta
				delta = max(delta, np.abs(best_action_val - V[s]))
				# add to utilities list
				V[s] = best_action_val
		# add utilities to class variable -> slow and dumb but it works
		for u in range(len(self.utilities)):
			state = self.all_states[u]
			self.utilities[state] = V[u]

	def policy(self, state):
		possible_actions = self.env.available_actions(state)
		numbers_left, dice_summation = state
		# Initialize with give up directly
		max_utility = self.giveup_reward(numbers_left)
		best_action = []
		A = np.zeros(len(self.env.available_actions(state)))
		for a in range(len(possible_actions)):
			# Finish this part - Find the best action with utility computed in value iteration
			prob = self.env.all_transition_next(state[0], self.env.available_actions(state)[a])[a-1][1]
			A[a] += prob * (max_utility + 1.0 * self.utilities[state])

		best_action_val = np.max(A)
		best_action_ind = np.where(A == best_action_val)[0]
		for i in best_action_ind:
			best_action.append(self.env.available_actions(state)[i])
			
		return best_action


if __name__=='__main__':
	env = Environment()
	# Try the following commands before coding
	# print(env.available_actions(State([1,2,3,4,5,6,7,8,9], 12)))
	# print(env.all_transition_next([1,2,3,4,5,6,7,8,9], [1,2]))

	agent = Agent(env)
	# Q1: Complete the Value iteration code here!
	agent.value_iteration()
	print('Utility of [1,2,3,4,5,6,7,8,9], 12: %.3f' % agent.utilities[State([1,2,3,4,5,6,7,8,9], 12)])
	print('Utility of [1,3,4,5,6,7,8,9], 12: %.3f' % agent.utilities[State([1,3,4,5,6,7,8,9], 12)])
	print('Utility of [1,3,5,6,7,8,9], 12: %.3f' % agent.utilities[State([1,3,5,6,7,8,9], 12)])
	
	# Q2: Complete policy function and run the code here!
	print('Optimal action of [1,2,3,4,5,6,7,8,9], 12: %s' % str(agent.policy(State([1,2,3,4,5,6,7,8,9], 12))))
	print('Optimal action of [1,3,4,5,6,7,8,9], 12: %s' % str(agent.policy(State([1,3,4,5,6,7,8,9], 12))))
	print('Optimal action of [1,3,5,6,7,8,9], 12: %s' % str(agent.policy(State([1,3,5,6,7,8,9], 12))))