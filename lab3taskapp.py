import collections.abc
import contextlib
import io
import random

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from ourMaze import ourMaze, mazeLocations
from src.graphClass import Graph
from src.agents import ProblemSolvingNavAgentBFS
from TreasureClass import Treasure
from TreasureMazeEnviornmentClass import TreasureMazeEnviornment

ARROWS = {'North': '↑', 'East': '→', 'South': '↓', 'West': '←'}
SCALE = 150

VERSIONS = {
  'Basic': 'Reach the finish',
  'Specific treasure': 'Find the Gold and then reach the finish',
  'Treasure collection': 'Collect ALL treasures and reach the finish',
}

mazeGraph = Graph(ourMaze)


def quiet(fn, *args):
  out = io.StringIO()
  with contextlib.redirect_stdout(out):
    fn(*args)
  return [line for line in out.getvalue().splitlines()
          if line and not line.startswith(('<Node', 'Solution', 'goal list', 'I have', 'current', 'step '))]


def place_treasures():
  validNodes = [n for n in mazeGraph.nodes() if n != 'S' and n != 'F']
  treasures = [Treasure('Gold'), Treasure('Diamond'), Treasure('Pizza'), Treasure('Points')]
  return dict(zip(random.sample(validNodes, 4), treasures))


def goal_for(version, treasureLocations):
  if version == 'Basic':
    return 'F'
  if version == 'Specific treasure':
    gold = [node for node, t in treasureLocations.items() if t.name == 'Gold'][0]
    return [gold, 'F']
  return list(treasureLocations) + ['F']


def new_run(version):
  treasureLocations = place_treasures()
  env = TreasureMazeEnviornment(mazeGraph, dict(treasureLocations), mazeLocations)
  agent = ProblemSolvingNavAgentBFS('S', mazeGraph, goal_for(version, treasureLocations))
  log = quiet(env.add_thing, agent)
  st.session_state[version] = {
    'env': env,
    'agent': agent,
    'targets': list(agent.targets),
    'visited': ['S'],
    'steps': 0,
    'log': log,
  }


def step_run(version):
  run = st.session_state[version]
  env, agent = run['env'], run['agent']
  if not env.is_agent_alive(agent):
    return
  run['log'] = quiet(env.step)
  run['steps'] += 1
  if agent.state not in run['visited']:
    run['visited'].append(agent.state)


def draw_maze(run):
  env, agent = run['env'], run['agent']
  net = Network(bgcolor='#242020', font_color='white', height='650px', width='100%', cdn_resources='remote')
  for node in mazeGraph.nodes():
    col, row = mazeLocations[node]
    label, color = node, '#97c2fc'
    if node in run['visited']:
      color = 'orange'
    if node in env.treasureLocations:
      treasure = env.treasureLocations[node]
      label = f'{node}: {treasure.name}'
      color = 'gold' if node in run['targets'] else '#8a7f4a'
    if node == 'S':
      color = '#008000'
    if node == 'F':
      color = '#800000'
    if node == agent.state:
      label = f'{label} {ARROWS[agent.heading]}'
      color = '#e040fb'
    net.add_node(node, label=label, color=color, x=col * SCALE, y=row * SCALE, physics=False, shape='square', size=20)
  for node in mazeGraph.nodes():
    for neighbor in mazeGraph.get(node):
      walked = node in run['visited'] and neighbor in run['visited']
      net.add_edge(node, neighbor, width=6, color='orange' if walked else '#5b7fa6')
  components.html(net.generate_html(), height=680)


def show_tab(version):
  if version not in st.session_state:
    new_run(version)
  run = st.session_state[version]
  agent = run['agent']

  st.subheader(f'{version}: {VERSIONS[version]}')

  if st.button("Run One Agent's Step", key=f'step-{version}', disabled=not agent.alive):
    step_run(version)

  m1, m2, m3, m4 = st.columns(4)
  m1.metric('Position', agent.state)
  m2.metric('Facing', f'{ARROWS[agent.heading]} {agent.heading}')
  m3.metric('Performance', agent.performance)
  m4.metric('Steps', run['steps'])

  collected = ', '.join(t.name for t in agent.collected) or 'nothing yet'
  st.info(f'Collected: {collected}')

  for line in run['log']:
    st.write(line)

  if not agent.alive:
    if agent.state == 'F':
      st.success(f'The agent reached the exit with performance {agent.performance}.')
    else:
      st.error(f'The agent ran out of performance at {agent.state}.')

  draw_maze(run)
  st.caption('Green: start · Red: exit · Gold: target treasure · Brown: other treasure · Orange: visited · Purple: agent (arrow = facing)')


def main():
  st.set_page_config(page_title='Treasure Maze', layout='wide')
  st.title('Problem Solving Agents: Treasure Maze')
  tabs = st.tabs(list(VERSIONS))
  for tab, version in zip(tabs, VERSIONS):
    with tab:
      show_tab(version)


if __name__ == '__main__':
  main()
