import time
from agent import Agent

class Environment:
    def __init__(self) -> None:
        raise NotImplementedError("Environment.__init__")

    def add_agent(self, agent: Agent) -> None:
        """
        Default is a single-agent environment. Override if you need multiple agents.

        Args:
            agent (Agent): the agent to add to the environment
        """
        self.agent = agent

    def run_simulation(self, steps: int, delay: int, display: bool = True) -> None:
        """
        Run a simulation of the environment for a certain number of time steps.
        This is a discrete time simulation; pretend that each "step" takes delay
        seconds.

        At each step the single agent is given a percept and asked for an action. 
        That action is used to update the environment.
        Args:
            steps (int): The number of time steps to perform
            delay (int): The number of seconds to pause between steps
            display (bool, optional): Whether to update the display at each step. 
        """
        if not self.agent:
            return
        
        for _ in range(steps):
            percept = self.get_percept(self.agent)
            action = self.agent.next_action(percept)
            self.perform_action(self.agent, action)
            if display:
                self.update_display()
                time.sleep(delay)

    def perform_action(self, agent: Agent, action) -> None:
        """
        Override to update the state of the environment based on the given action 
        by the specified agent.

        Args:
            agent (Agent): The agent performing the action
            action: The action performed. Typically some sort of dictionary.
        """
        raise NotImplementedError("Environment.perform_action")

    def update_display(self) -> None:
        """
        Override to display the current environment.
        """
        raise NotImplementedError("Environment.update_display")

    def get_percept(self, agent: Agent):
        """
        Override to return the current percept for the given agent

        Args:
            agent (Agent): the agent who needs a percept

        Returns:
            the current percept for the given agent.
        """
        raise NotImplementedError("Environment.get_percept")
