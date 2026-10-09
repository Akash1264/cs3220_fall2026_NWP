from src.environmentClass import Environment
from src.thingClass import Thing
from src.locations import *

class environmentPro(Environment):
  def __init__(self):
    super().__init__()
    self.things = [] #new prop 

  #Return all things exactly at a given location
  def list_things_at(self, location, thingClass=Thing):
    return [thing for thing in self.things if thing.location == location and isinstance(thing, thingClass)]

  def add_thing(self, thing, location=None): # improved  (pro) - version 
    from src.agentClass import Agent
    if thing in self.agents:
      print("Can't add the same agent twice")
    else:
      if isinstance(thing, Agent):
        thing.performance = 0
        thing.location = location if location is not None else self.default_location(thing)
        self.agents.append(thing)
        print(f"Welcome! You are added in location {thing.location}")
    if thing in self.things and thing.location==location:
      print("Can't add the same agent twice")
    else:
      if not isinstance(thing, Agent):
        thing.location = location if location is not None else self.default_location(thing)
        self.things.append(thing)
  
  def delete_thing(self, thing):
    if thing in self.agents:
      self.agents.remove(thing)
    else:
      self.things.remove(thing)

  def is_agent_alive(self, agent): # improved  (pro) - version 
    return agent.alive

  def update_agent_alive(self, agent): #new method used by is_done() method of the parent (Environment) class
    if agent.performance <= 0:
      agent.alive = False
      print("Agent {} is dead.".format(agent))
