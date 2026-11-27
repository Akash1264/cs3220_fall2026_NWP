'''
A base class representing an abstract Environment.
'Real' Environment classes must inherit from this one.
The environment keeps a list of .agents.
Each agent has a .performance slot, initialized to 0.
'''

#from agentClass import Agent

class Environment:
  def __init__(self):
    self.agents = []

  def percept(self, agent):
    #Return the percept that the agent sees at this point. (Implement this in derived classes)
    print("I don't know how to percept.")

  def execute_action(self, agent, action):
    #Change the world to reflect this action. (Implement this in derived classes)
    print("I don't know how to execute_action.")

  def default_location(self, thing):
    #Default location to place a new thing with unspecified location.
    return None

  def is_done(self):
    #By default, we're done when we can't find a live agent.
    return not any(agent.alive for agent in self.agents)

  def step(self): # implementation should be in spec. env. for problem Solving Agents
    pass
        #Run the environment for one time step.
        # if not self.is_done():
        #     actions = []
        #     for agent in self.agents:
        #         if agent.alive:
                    #action=agent(self.percept(agent))
                    #print(self.percept(agent))
                    # action=agent.program(self.percept(agent))
                    # print("Agent percepted {}.".format(self.percept(agent)))
                    # print("Agent decided to do {}.".format(action))
        #             actions.append(action)
        #         else:
        #             actions.append("")
        #     for (agent, action) in zip(self.agents, actions):
        #         self.execute_action(agent, action)
        # else:
        #   print("There is no one here who could work...")

  def run(self, steps=10):
        #Run the Environment for given number of time steps.
        for step in range(steps):
            if self.is_done():
                return
            print("step {0}:".format(step+1))
            self.step()

  def add_thing(self, thing, location=None):
    #from agentClass import Agent
    from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
    if thing in self.agents:
      print("Can't add the same agent twice")
    else:
      if isinstance(thing, SimpleProblemSolvingAgentProgram):
        thing(thing.state)
        #thing.performance = 0
        #thing.location = location if location is not None else self.default_location(thing)
        print(f"The Agent in {thing.state} with performance {thing.performance}")
        self.agents.append(thing)
        
       
            
          

  def delete_thing(self, thing):
    if thing in self.agents:
      self.agents.remove(thing)
