from src.environmentClass import Environment


class MazeNavigationEnvironment(Environment):
  def __init__(self, navGraph):
    super().__init__()
    self.status = navGraph
    

  def percept(self, agent):
    #Returns the agent's location, and the location status (Dirty/Clean).
    return agent.state

  def is_agent_alive(self, agent):
    return agent.alive

  def update_agent_alive(self, agent):
    if agent.performance <= 0:
      agent.alive = False
      print("Agent {} is dead.".format(agent))
    elif agent.state==agent.goal or len(agent.seq)==0:
      agent.alive = False
      if len(agent.seq)==0:
        print("Agent reached all goals")
      else:
        print(f"Agent reached the goal: {agent.goal}")
      

  def execute_action(self, agent, action):
    '''Check if agent alive, if so, execute action'''
    if self.is_agent_alive(agent):
        """Change agent's location -> agent's state;
        Track performance.
        -1 for each move."""
        agent.state=agent.update_state(agent.state, action)
        agent.performance -= 1
        print(f"Agent in {agent.state} with performance = {agent.performance}")
        self.update_agent_alive(agent)

        # if action == 'Right':
        #     agent.location = loc_B
        #     agent.performance -= 1
        #     self.update_agent_alive(agent)
        # elif action == 'Left':
        #     agent.location = loc_A
        #     agent.performance -= 1
        #     self.update_agent_alive(agent)
        # elif action == 'Suck':
        #     if self.status[agent.location] == 'Dirty':
        #         agent.performance += 10
        #     self.status[agent.location] = 'Clean'

  # def default_location(self, thing):
  #       """Agents start in either location at random."""
  #       print("Agent is starting in random location...")
  #       return random.choice([loc_A, loc_B])
  
  def step(self):
    if not self.is_done():
        actions = []
        for agent in self.agents:
          if agent.alive:
            #with agent.state because for PS Agent we don't need to percive
            action=agent.seq.pop(0)
            print("Agent decided to do {}.".format(action))
            actions.append(action)
          else:
            actions.append("")
            
        for (agent, action) in zip(self.agents, actions):
          self.execute_action(agent, action)
    else:
        print("There is no one here who could work...")
    