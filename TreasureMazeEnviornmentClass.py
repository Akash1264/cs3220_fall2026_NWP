from src.environmentClass import Environment
from src.graphClass import Graph

HEADINGS = ['North', 'East', 'South', 'West']

class TreasureMazeEnviornment(Environment):
  def __init__(self, graph: Graph, treasure_locations: dict, locations: dict, treasure_bonus=10):
    super().__init__()
    self.treasureBonus = treasure_bonus
    self.graph = graph
    self.treasureLocations = treasure_locations
    self.locations = locations

  def direction(self, fromNode, toNode):
    fx, fy = self.locations[fromNode]
    tx, ty = self.locations[toNode]
    if tx > fx: return 'East'
    if tx < fx: return 'West'
    if ty < fy: return 'North'
    return 'South'

  def path_to_actions(self, start, heading, path):
    actions = []
    current = start
    for nextNode in path:
      want = self.direction(current, nextNode)
      turns = (HEADINGS.index(want) - HEADINGS.index(heading)) % 4
      if turns == 1:
        actions.append('right')
      elif turns == 3:
        actions.append('left')
      elif turns == 2:
        actions += ['right', 'right']
      actions.append('advance')
      heading = want
      current = nextNode
    return actions

  def add_thing(self, thing, location=None):
    if thing in self.agents:
      print("Can't add the same agent twice")
      return
    thing.performance = len(self.graph.nodes()) // 2
    thing.collected = []
    thing.targets = thing.goal[:-1] if isinstance(thing.goal, list) else []
    thing.heading = 'North'
    self.agents.append(thing)
    thing(thing.state)
    print(f'Route: {thing.seq}')
    thing.seq = self.path_to_actions(thing.state, thing.heading, thing.seq)
    print(f'Agent at {thing.state} facing {thing.heading} with performance {thing.performance}')
    print(f'Actions: {thing.seq}')

  def execute_action(self, agent, action):
    agent.performance -= 1
    if action == 'left':
      agent.heading = HEADINGS[(HEADINGS.index(agent.heading) - 1) % 4]
      print(f'Agent turned left, now facing {agent.heading}, performance = {agent.performance}')
    elif action == 'right':
      agent.heading = HEADINGS[(HEADINGS.index(agent.heading) + 1) % 4]
      print(f'Agent turned right, now facing {agent.heading}, performance = {agent.performance}')
    elif action == 'advance':
      ahead = [n for n in self.graph.get(agent.state) if self.direction(agent.state, n) == agent.heading]
      if not ahead:
        print(f'Agent bumped into a wall at {agent.state}, performance = {agent.performance}')
        return
      agent.state = ahead[0]
      print(f'Agent advanced {agent.heading} to {agent.state}, performance = {agent.performance}')
     if agent.state in self.treasureLocations:
        treasure = self.treasureLocations.pop(agent.state)
        agent.collected.append(treasure)
        agent.performance += self.treasureBonus
        print(f'Agent grabbed {treasure}! +{self.treasureBonus} performance, now {agent.performance}')

  def step(self):
    actions = []
    if self.is_done():
      print("There is no one here who could work...")
      return actions
    for agent in self.agents:
      if not agent.alive:
        continue
      action = agent.seq.pop(0)
      actions.append(action)
      self.execute_action(agent, action)
      if not agent.seq:
        print(f'Agent reached the exit with {agent.collected}')
        agent.alive = False
      elif agent.performance <= 0:
        print('Agent ran out of performance and died')
        agent.alive = False
    return actions

  def is_done(self):
    return not any(agent.alive for agent in self.agents)

  def is_agent_alive(self, agent):
    return agent.alive

  def run(self, steps=50):
    step = 0
    while not self.is_done() and step < steps:
      step += 1
      print(f'step {step}:')
      self.step()
