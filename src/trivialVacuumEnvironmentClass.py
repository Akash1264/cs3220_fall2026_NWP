from src.environmentClass import Environment
from src.locations import *

import random

class TrivialVacuumEnvironment(Environment):
  def __init__(self):
    super().__init__()
    self.status = {loc_A: random.choice(['Clean', 'Dirty']),
                   loc_B: random.choice(['Clean', 'Dirty'])}

  def percept(self, agent):
    #Returns the agent's location, and the location status (Dirty/Clean).
    return agent.location, self.status[agent.location]

  def is_agent_alive(self, agent):
    return agent.alive

  def update_agent_alive(self, agent):
    if agent.performance <= 0:
      agent.alive = False
      print("Agent {} is dead.".format(agent))

  def execute_action(self, agent, action):
    '''Check if agent alive, if so, execute action'''
    if self.is_agent_alive(agent):
        """Change agent's location and/or location's status;
        Track performance.
        Score 10 for each dirt cleaned; -1 for each move."""

        if action == 'Right':
            agent.location = loc_B
            agent.performance -= 1
            self.update_agent_alive(agent)
        elif action == 'Left':
            agent.location = loc_A
            agent.performance -= 1
            self.update_agent_alive(agent)
        elif action == 'Suck':
            if self.status[agent.location] == 'Dirty':
                agent.performance += 10
                self.status[agent.location] = 'Clean'
            else:
              agent.performance -= 1
            self.update_agent_alive(agent)

  def default_location(self, thing):
        """Agents start in either location at random."""
        print("Agent is starting in random location...")
        return random.choice([loc_A, loc_B])