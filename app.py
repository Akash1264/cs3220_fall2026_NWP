"""
EXPLAINED COPY of app.py - code identical to the real file.
CS3220 Lab 4 - Rescue Robots in a Hazardous Laboratory Maze (Streamlit version)

Run from the project folder:
    streamlit run app.py
How Streamlit works: the WHOLE script runs top to bottom every time you change a widget
(slider, button, ...). Each st.something(...) call puts one element on the page.
"""
import io                                             # StringIO: catch printed text in memory
import os                                             # build file paths
import random                                         # random seed for "New random maze"
import tempfile                                       # temporary folder for the pyvis HTML
import contextlib                                     # redirect_stdout: send print() output into the log

import matplotlib.pyplot as plt                       # maze pictures
import pandas as pd                                   # tables
import streamlit as st                                # the web app framework
import streamlit.components.v1 as components          # to embed the pyvis HTML graph

from src.labMazeData import (makeLabMaze, makeLabTransitionModel, makeDecisionGraph,     # maze + models
                             labStatesLocations, findCells, FREE, WALL, DRONE, TARGET, START,
                             ACTION_NAMES, ACTION_COSTS)
from src.labMazeGraphClass import labMazeGraph        # state-space graph
from src.droneClass import makeDrones                 # drones
from src.labEnvironmentClass import LabEnvironment    # the lab environment
from src.agents import RescueRobotAgentUCS, RescueRobotAgentIDS   # the two robots
from src.labVisualization import drawLabMaze, labStateSpaceNetwork, decisionGraphNetwork   # drawing

st.set_page_config(page_title="Lab 4 - Rescue Robots", page_icon="🤖", layout="wide")   # tab title, icon, full width

UCS_COLOR, IDS_COLOR = "#4169e1", "#ff8c00"   # royal blue, dark orange  (colours of the two robots)


# ---------------------------------------------------------------------------
# Model building and simulation
# ---------------------------------------------------------------------------
def build_world(n, wall_ratio, drone_ratio, seed):    # Task 1: build everything for one maze
    maze, start, target = makeLabMaze(n, wall_ratio=wall_ratio, drone_ratio=drone_ratio, seed=seed)   # random lab
    tm = makeLabTransitionModel(maze)                 # transition model {cell: {action: next cell}}
    graph = labMazeGraph(tm, labStatesLocations(list(tm.keys())))   # state-space graph + positions
    drones = makeDrones(findCells(maze, DRONE), len(graph.nodes()), seed=seed)   # one drone per drone cell
    key_nodes, dgraph = makeDecisionGraph(tm, start, target)         # junction graph
    return dict(maze=maze, start=start, target=target, tm=tm, graph=graph,   # bundle it all in one dict
                drones=drones, key_nodes=key_nodes, dgraph=dgraph)


def simulate(world, seed):                            # Task 2: race both robots in one environment
    """Run both agents in one environment. Records energy and position after every step."""
    drones = makeDrones(findCells(world["maze"], DRONE), len(world["graph"].nodes()), seed=seed)   # fresh drones
    env = LabEnvironment(world["maze"], world["graph"], drones)       # the lab
    ucs = RescueRobotAgentUCS(world["start"], world["graph"], world["target"], name="UCS-Robot")   # robot 1
    ids = RescueRobotAgentIDS(world["start"], world["graph"], world["target"], name="IDS-Robot")   # robot 2
    robots = [ucs, ids]

    log = io.StringIO()                               # all printed messages go here (shown in "Full agent log")
    history = [{r.name: (r.state, r.energy) for r in robots}]   # step 0: position and energy of each robot
    with contextlib.redirect_stdout(log):             # everything printed inside this block goes into `log`
        for r in robots:
            env.add_thing(r)                          # add robot -> it searches and gets its plan
        print("\n--- execution ---")
        for step in range(200):                       # at most 200 steps
            if env.is_done():                         # both robots finished?
                print(f"--- all agents finished after {step} steps ---")
                break
            print(f"step {step + 1}:")
            env.step()                                # both robots do one action
            history.append({r.name: (r.state, r.energy) for r in robots})   # record for replay + energy chart
    return robots, drones, history, log.getvalue()    # everything the page needs


def winner_text(robots):                              # who won?
    finished = [r for r in robots if r.status == "rescued"]   # only robots that reached the target count
    if not finished:
        return None, "No winner: neither robot reached the rescue target."
    best = max(r.energy for r in finished)            # highest remaining energy
    top = [r for r in finished if abs(r.energy - best) < 1e-9]   # robots with that energy (could be both)
    if len(top) > 1:
        return "tie", f"Tie: both robots reached the target with {best:.2f} energy."
    return top[0].name, f"{top[0].name} wins: reached the target with {best:.2f} energy left."


def results_table(robots):                            # one row of results per robot
    return pd.DataFrame([{
        "Robot": r.name,
        "Reached target": "yes" if r.status == "rescued" else "no",
        "Final status": r.status,                     # rescued / captured / out of energy / ...
        "Energy left": round(r.energy, 2),
        "Moves": r.steps,
        "Drones met": len(r.known_drones),
        "Defense Mode used": r.defense_activations,
        "Re-plans": r.replans,
        "Nodes expanded (first search)": r.search_log[0].get("expanded") if r.search_log else None,
        "Nodes expanded (all searches)": sum(s.get("expanded", 0) for s in r.search_log),
    } for r in robots]).set_index("Robot")            # robot name as the row label


def pyvis_html(builder, *args):                       # get a pyvis graph as HTML text
    """Build a pyvis network into a temp file and return its HTML."""
    with tempfile.TemporaryDirectory() as d:          # temporary folder (deleted afterwards)
        path = os.path.join(d, "graph.html")          # temp file path
        builder(*args, path)                          # labStateSpaceNetwork(...) or decisionGraphNetwork(...)
        with open(path, encoding="utf-8") as f:
            return f.read()                           # return the file's HTML text


@st.cache_data(show_spinner=False)                    # remember results: same settings -> no re-run
def batch_compare(n_mazes, n, wall_ratio, drone_ratio):   # race on many mazes
    rows = []
    for seed in range(n_mazes):                       # maze number 0, 1, 2, ...
        for with_drones in (True, False):             # once with drones, once without
            w = build_world(n, wall_ratio, drone_ratio, seed)
            if not with_drones:
                w["maze"] = w["maze"].copy()          # copy so the original isn't changed
                w["maze"][w["maze"] == DRONE] = FREE   # same maze, drones removed
            robots, _, _, _ = simulate(w, seed)       # race
            win, _ = winner_text(robots)              # who won
            rows.append({"drones": "with drones" if with_drones else "without drones",
                         "winner": {None: "no winner", "tie": "tie"}.get(win, win),
                         "UCS expanded": robots[0].search_log[0].get("expanded"),
                         "IDS expanded": robots[1].search_log[0].get("expanded")})
    return pd.DataFrame(rows)                         # one row per race


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
if "seed" not in st.session_state:                    # first time the page loads
    st.session_state.seed = 181                       # start with the notebook's maze

with st.sidebar:                                      # everything below appears in the left sidebar
    st.header("Laboratory settings")
    n = st.slider("Maze size (n × n)", 5, 10, 7)      # slider from 5 to 10, default 7
    wall_pct = st.slider("Walls / debris (%)", 10, 35, 25)
    drone_pct = st.slider("Security drones (%)", 0, 20, 10)
    st.number_input("Seed (same seed = same maze)", min_value=0, max_value=1_000_000, step=1, key="seed")
    # key="seed" links this box to st.session_state.seed
    def _new_seed():                                  # runs when the button is clicked
        st.session_state.seed = random.randint(0, 1_000_000)   # pick a random seed
    st.button("New random maze", on_click=_new_seed)
    st.caption("Seed 181 with the default settings is the maze used in the notebook.")

seed = int(st.session_state.seed)                     # current seed
try:
    world = build_world(n, wall_pct / 100, drone_pct / 100, seed)   # build the maze (percent -> ratio)
except RuntimeError:                                  # no solvable maze possible with these settings
    st.error("Couldn't generate a maze where the target is reachable. Lower the wall percentage or change the seed.")
    st.stop()                                         # stop drawing the rest of the page

maze, graph, drones = world["maze"], world["graph"], world["drones"]   # short names
n_nodes = len(graph.nodes())                          # number of states

st.title("Rescue Robots in a Hazardous Laboratory")   # page title
st.write("Two robots start in the same cell and race to the rescue target. "
         "One plans with Uniform-Cost Search, the other with Iterative Deepening. "
         "Neither knows where the security drones are until it runs into one.")

tab_maze, tab_model, tab_race, tab_compare = st.tabs(  # create 4 tabs
    ["The laboratory", "Problem model", "Run the robots", "Compare on many mazes"])

# ---------------------------------------------------------------------------
# Tab 1 - maze
# ---------------------------------------------------------------------------
with tab_maze:                                        # content of tab 1
    left, right = st.columns([3, 2])                  # two columns, left wider
    with left:
        fig, ax = plt.subplots(figsize=(6.5, 6.5))    # new figure
        drawLabMaze(maze, drones, ax=ax, title=f"{n} × {n} laboratory maze (seed {seed})")   # draw the maze
        st.pyplot(fig)                                # show it on the page
        plt.close(fig)                                # free memory
    with right:
        st.subheader("Maze matrix")
        st.code(str(maze), language=None)             # the NumPy grid as text
        counts = pd.DataFrame([                       # table: how many cells of each type
            {"Code": c, "Cell type": name, "Cells": int((maze == c).sum()),
             "Share": f"{(maze == c).mean():.0%}"}
            for c, name in [(FREE, "free"), (WALL, "wall / debris"), (DRONE, "security drone"),
                            (TARGET, "rescue target"), (START, "start")]
        ]).set_index("Code")
        st.dataframe(counts)
        st.write(f"Start: **{world['start']}**, target: **{world['target']}**")

        st.subheader("Security drones")
        st.caption(f"Attack power is random between 10% and 40% of the {n_nodes} graph nodes "
                   f"({0.1 * n_nodes:.1f} to {0.4 * n_nodes:.1f}).")
        st.dataframe(pd.DataFrame([{"Location": str(d.location), "Attack power": d.attack_power}
                                   for d in drones]), hide_index=True)   # one row per drone

# ---------------------------------------------------------------------------
# Tab 2 - problem model
# ---------------------------------------------------------------------------
with tab_model:
    st.subheader("Actions and costs")
    st.dataframe(pd.DataFrame([{"Action": a, "Movement": ACTION_NAMES[a], "Cost": ACTION_COSTS[a]}
                               for a in ACTION_NAMES]), hide_index=True)   # the action table

    c1, c2, c3 = st.columns(3)                        # three number boxes side by side
    c1.metric("States (non-wall cells)", n_nodes)
    c2.metric("Available actions (edges)", sum(len(v) for v in graph.origin.values()))
    c3.metric("Decision-graph nodes", len(world["key_nodes"]))

    st.subheader("Transition model")
    cell = st.selectbox("Pick a state to see RESULT(s, a) for each available action",   # dropdown of cells
                        sorted(world["tm"].keys()),
                        index=sorted(world["tm"].keys()).index(world["start"]))       # start selected first
    st.dataframe(pd.DataFrame([{"Action": f"{a}: {ACTION_NAMES[a]}", "Next state": str(s2),
                                "Cost": ACTION_COSTS[a]} for a, s2 in world["tm"][cell].items()]),
                 hide_index=True)                     # RESULT(cell, a) for each legal action

    st.subheader("Graphs")
    which = st.radio("Graph to show", ["Decision graph (start, target, junctions)",
                                       "Full state space (every action)"], horizontal=True)   # choice
    if which.startswith("Decision"):
        html = pyvis_html(decisionGraphNetwork, world["dgraph"], world["start"], world["target"],
                          graph.locations)            # build the junction graph
    else:
        html = pyvis_html(labStateSpaceNetwork, graph, maze)   # build the full graph
    components.html(html, height=780, scrolling=True) # show the interactive graph inside the page

# ---------------------------------------------------------------------------
# Tab 3 - race
# ---------------------------------------------------------------------------
with tab_race:
    robots, sim_drones, history, log = simulate(world, seed)   # run the race
    ucs, ids = robots
    win, msg = winner_text(robots)                    # who won
    if win is None:
        st.warning(msg)                               # yellow box: no winner
    else:
        st.success(msg)                               # green box: winner or tie

    st.dataframe(results_table(robots))               # results table

    left, right = st.columns([3, 2])
    with left:
        last = len(history) - 1                       # number of the last step
        step = st.slider("Replay step", 0, last, last) if last > 0 else 0   # choose a step to view
        snap = history[step]                          # positions + energy at that step
        paths = {}
        for r, color in ((ucs, UCS_COLOR), (ids, IDS_COLOR)):
            k = min(step, len(r.path) - 1)            # a finished robot's path stops growing
            paths[f"{r.name} ({snap[r.name][1]:.1f} energy)"] = (r.path[:k + 1], color)   # path up to that step
        fig, ax = plt.subplots(figsize=(6.5, 6.8))
        drawLabMaze(maze, sim_drones, paths=paths, ax=ax, title=f"Robot paths after step {step}")
        st.pyplot(fig)
        plt.close(fig)
    with right:
        st.subheader("Energy over time")
        energy = pd.DataFrame({r.name: [h[r.name][1] for h in history] for r in robots})   # energy per step
        energy.index.name = "step"
        st.line_chart(energy, color=[UCS_COLOR, IDS_COLOR])   # line chart, one line per robot
        st.caption("Each move costs its action cost. A drone encounter in Defense Mode costs 10% of current energy.")

        st.subheader("Planned routes")
        for r in robots:
            first = r.search_log[0] if r.search_log else {}   # stats of the first search
            st.write(f"**{r.name}** expanded {first.get('expanded', '?')} nodes for its first plan "
                     f"and re-planned {r.replans} time(s).")

    with st.expander("Full agent log"):               # collapsible box
        st.code(log, language=None)                   # all printed messages from the race

# ---------------------------------------------------------------------------
# Tab 4 - batch comparison
# ---------------------------------------------------------------------------
with tab_compare:
    st.write("A single maze can be lucky for either robot. Run the same race on many random mazes, "
             "with the drones and again on the same mazes without them.")
    n_mazes = st.slider("Number of mazes", 20, 500, 100, step=20)   # how many mazes
    if st.button("Run comparison"):                   # only runs when clicked
        with st.spinner(f"Racing on {n_mazes} mazes…"):   # loading indicator
            df = batch_compare(n_mazes, n, wall_pct / 100, drone_pct / 100)
        outcome = (df.groupby(["drones", "winner"]).size().unstack(fill_value=0))
        # count wins: rows = with/without drones, columns = UCS / IDS / tie / no winner
        st.subheader("Who wins")
        st.dataframe(outcome)
        st.subheader("Search effort (nodes expanded for the first plan)")
        st.dataframe(df[df["drones"] == "with drones"][["UCS expanded", "IDS expanded"]]
                     .describe().loc[["mean", "50%", "max"]].round(1))   # average, median, max
        st.info("Without drones the robots tie on almost every maze: on a grid the fewest-moves route is "
                "also the cheapest for these costs. With drones, the winner depends on which drones "
                "each route happens to cross. UCS always needs far fewer node expansions.")
