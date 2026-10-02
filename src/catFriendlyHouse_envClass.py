import random
from src.environmentProClass import environmentPro
from src.thingClass import Thing
from src.locations import *

from src.catFriendlyHouse_membersClass import Food,Milk,Sausage,Mouse,Dog

from src.agentClass import Agent, proCatAgent, MouseAgent


#catFriendlyHouse_envClass
class catFriendlyHouse_env(environmentPro):
  def __init__(self):
    super().__init__()
    self.locations=[loc_A, loc_B, loc_C]

  def default_location(self, thing):
    print("The item is starting in random location...")
    return random.choice(self.locations)
  
    
  

  def room_state(self, location):
    items = [type(t).__name__ for t in self.list_things_at(location, thingClass=Food)]
    if len(items) == 0:
      return 'Empty'
    if len(items) == 1:
      return items[0]
    return items

  def percept(self, agent):
    self.status = {loc: self.room_state(loc) for loc in self.locations}
    return agent.location, self.status[agent.location]

  def execute_action(self, agent, action):
    #changes the state of the environment based on what the agent does.
    if not self.is_agent_alive(agent):
      return

    if action == 'Drink':
      milk = self.list_things_at(agent.location, thingClass=Milk)[0]
      if agent.drink(milk):
        print(f"The Cat drank {milk} at location: {agent.location}")
        self.delete_thing(milk)

    elif action == 'Eat':
      sausage = self.list_things_at(agent.location, thingClass=Sausage)[0]
      if agent.eat(sausage):
        print(f"The Cat ate {sausage} at location: {agent.location}")
        self.delete_thing(sausage)

    elif action == 'Catch':
      mouse = self.list_things_at(agent.location, thingClass=Mouse)[0]
      if agent.catch(mouse):
        print(f"The Cat caught {mouse} at location: {agent.location}")
      else:
        print(f"The Cat is too weak (performance: {agent.performance}) - the Mouse survived and ran away!")
      self.delete_thing(mouse)

    elif action == 'GoAhead':
      i = self.locations.index(agent.location)
      if agent.direction and i == len(self.locations) - 1:
        agent.changeDirection()
        print("Last room! Some items are still there -> the Cat turns around (Right to Left)")
      elif not agent.direction and i == 0:
        print("The Cat is back in the first room. The hunt is over!")
        agent.alive = False
        return
      agent.location = self.locations[i + 1 if agent.direction else i - 1]
      agent.performance -= 1
      print(f"The Cat moved to location: {agent.location}")

  def is_done(self):
    no_agents = not any(agent.is_alive() for agent in self.agents)
    no_food = len(self.list_things_at_all(Food)) == 0
    return no_agents or no_food

  def list_things_at_all(self, thingClass):
    return [t for t in self.things if isinstance(t, thingClass)]



#catFriendlyHouse_envClass
class catFriendlyHouse2_env(environmentPro):
  def __init__(self):
    super().__init__()
    self.locations=[loc_A, loc_B, loc_C, loc_D]

  def default_location(self, thing):
    print("The item is starting in random location...")
    return random.choice(self.locations)
  
  #Return all agents exactly at a given location
  def list_agents_at(self, location, thingClass=Thing):
    return [a for a in self.agents
            if a.location == location and isinstance(a, thingClass)
            and not getattr(a, 'eaten', False)]

  def percept(self, agent):
    #return a list of things AND a list of agents that are in our agent's location
    agents = [a for a in self.list_agents_at(agent.location) if a is not agent]
    things = self.list_things_at(agent.location)
    return agent.location, agents, things

  def add_thing(self, thing, location=None): # improved  
    # perf = original one not 0 like in parent class
    if thing in self.agents:
      print("Can't add the same agent twice")
    else:
      if isinstance(thing, Agent):
        thing.location = location if location is not None else self.default_location(thing)
        self.agents.append(thing)
        print(f"Welcome! You are added in location {thing.location}")
    if thing in self.things and thing.location==location:
      print("Can't add the same agent twice")
    else:
      if not isinstance(thing, Agent):
        thing.location = location if location is not None else self.default_location(thing)
        self.things.append(thing)

  def targets_left(self):
    #uneaten mice (even exhausted ones) + things (e.g. a Dog)
    mice = [a for a in self.agents if isinstance(a, MouseAgent) and not a.eaten]
    return mice + self.things

  def cat_alive_check(self, cat):
    if cat.performance <= 0:
      cat.alive = False
      print(f"Cat performance: {cat.performance} -> GAME OVER!")

  def move_cat(self, cat):
    #GoAhead: if the Cat is in the last room for its direction -> change direction first
    i = self.locations.index(cat.location)
    if (cat.direction and i == len(self.locations) - 1) or (not cat.direction and i == 0):
      cat.changeDirection()
    i = i + 1 if cat.direction else i - 1
    cat.location = self.locations[i]
    cat.performance -= 5
    print(f"The Cat moved to {cat.location} (performance: {cat.performance})")
    self.cat_alive_check(cat)
    
  def execute_action(self, agent, action):
    #changes the state of the environment based on what the agent does.
    if self.is_agent_alive(agent):
      #the current agent is Cat & Mouse is still there
      if isinstance(agent, proCatAgent) and len(self.targets_left())>0:
        print("Some items are still there ....")
        if action in ('Go ahead', 'Check direction'):
          self.move_cat(agent)

        elif action=='Catch':
          mice = self.list_agents_at(agent.location, MouseAgent)
          if not mice:
            print("The Mouse already ran away!")
            return
          mouse = mice[0]
          if agent.performance < mouse.performance * 5:
            agent.performance -= 10
            print(f"The Cat is too weak to catch the Mouse (cat: {agent.performance}, mouse: {mouse.performance})")
            self.cat_alive_check(agent)
          else:
            agent.performance += 10
            mouse.eaten = True
            mouse.alive = False
            print(f"The Cat caught and ate the Mouse at {agent.location}! (performance: {agent.performance})")

        elif action=='Fight':
          dogs = self.list_things_at(agent.location, Dog)
          if agent.performance >= 10:
            agent.performance += 20
            self.delete_thing(dogs[0])
            print(f"The Cat beat the Dog! (performance: {agent.performance})")
          else:
            agent.performance -= 10
            print(f"The Dog won... (performance: {agent.performance})")
            self.cat_alive_check(agent)

      elif isinstance(agent, MouseAgent):
        if agent.performance > 0:
          agent.location = action  #random room chosen by RandomAgentProgram
          agent.performance -= 1
          print(f"The Mouse moved to {agent.location} (performance: {agent.performance})")
        if agent.performance <= 0:
          agent.alive = False  #can't move anymore, but stays in its room for the Cat
          print(f"The Mouse is exhausted and stays at {agent.location}")

      else:
          print("There is nothing for Agent Cat here. Done!")
          agent.alive=False
    
  def is_done(self):
    cats = [a for a in self.agents if isinstance(a, proCatAgent)]
    if cats:
      return not any(c.is_alive() for c in cats)
    return not any(agent.is_alive() for agent in self.agents)
