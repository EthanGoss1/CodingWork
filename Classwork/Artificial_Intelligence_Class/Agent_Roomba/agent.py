class Agent:
	def next_action(self, percept):
		"""
		The controller function for this agent. Given the current percept and 
		whatever belief state is stored inside the agent, update the belief state
		and return the next action.

		Args:
			percept: The agent's next perception of its environment; typically a dictionary.

		
		Returns:
			An action for the environment to contemplate.

								
					
		"""
		raise NotImplementedError("Agent.next_action")
