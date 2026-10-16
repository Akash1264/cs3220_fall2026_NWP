"""EXPLAINED COPY of src/labVisualization.py - code identical to the real file.
Drawing helpers for the Hazardous Laboratory Maze (matplotlib + pyvis)."""
import matplotlib.pyplot as plt                       # matplotlib: draws the maze pictures
from matplotlib.patches import Rectangle              # one coloured square per cell
from src.labMazeData import (FREE, WALL, DRONE, TARGET, START,   # cell codes
                             ACTION_NAMES, intTupleTostr)          # action names, (2,3) -> "2-3"

CELL_COLORS = {FREE: "#eef3fb", WALL: "#555555", DRONE: "#f4a6a6",   # colour of each cell type:
               TARGET: "#f7dc6f", START: "#9fd8a3"}                  # light blue, grey, red, yellow, green
CELL_LABELS = {WALL: "WALL", TARGET: "TARGET", START: "START"}        # text written inside cells


def drawLabMaze(maze, drones=(), paths=None, decision_nodes=None, title="7 x 7 Laboratory Maze", ax=None):
    """Grid picture of the maze. paths = {label: (list_of_cells, color)}."""
    n = maze.shape[0]                                 # grid size
    if ax is None:                                    # no drawing area given?
        _, ax = plt.subplots(figsize=(7, 7))          # -> create a 7x7-inch figure
    attack = {d.location: d.attack_power for d in drones}   # cell -> drone attack power, for labels
    for i in range(n):                                # every row
        for j in range(n):                            # every column
            code = int(maze[i, j])                    # what is in this cell
            ax.add_patch(Rectangle((j, i), 1, 1, facecolor=CELL_COLORS[code], edgecolor="#333", lw=1))
            # draw a 1x1 square at x=column, y=row in the cell's colour
            if code == DRONE:                         # drone cell:
                txt = f"DRONE\natk {attack.get((i, j), '?')}"   # "DRONE / atk 10.15" ('?' if unknown yet)
            else:
                txt = CELL_LABELS.get(code, "")       # WALL / TARGET / START, or nothing
            if txt:
                ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=8,
                        color="white" if code == WALL else "black", weight="bold")   # write it centred
            if decision_nodes and (i, j) in decision_nodes and code != WALL:
                ax.plot(j + 0.15, i + 0.15, marker="D", color="purple", ms=6)   # purple diamond = junction
    if paths:                                         # robot paths to draw?
        offsets = [-0.12, 0.12, 0.0, 0.2]             # shift each path a little so they don't overlap
        for k, (label, (cells, color)) in enumerate(paths.items()):
            off = offsets[k % len(offsets)]           # this path's shift
            xs = [c[1] + 0.5 + off for c in cells]    # x = column of each cell's centre
            ys = [c[0] + 0.5 + off for c in cells]    # y = row of each cell's centre
            ax.plot(xs, ys, "-o", color=color, lw=2.5, ms=4, label=label, alpha=0.85)   # line with dots
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=len(paths))   # legend under the grid
    ax.set_xlim(0, n)                                 # show columns 0..n
    ax.set_ylim(n, 0)                                 # rows 0..n, flipped so row 0 is at the TOP
    ax.set_xticks([j + 0.5 for j in range(n)], [str(j) for j in range(n)])   # column numbers
    ax.set_yticks([i + 0.5 for i in range(n)], [str(i) for i in range(n)])   # row numbers
    ax.xaxis.tick_top()                               # column numbers on top, like the example picture
    ax.set_aspect("equal")                            # square cells
    ax.set_title(title, pad=24, weight="bold")        # title
    return ax


def labStateSpaceNetwork(labGraph, maze, filename="labStateSpace.html"):
    """pyvis picture of the full state space - every available action gets its own arrow.
    (Fixes the tutorial graph, which was undirected and lost the reverse action labels.)"""
    from pyvis.network import Network                 # pyvis: interactive graphs in the browser
    net = Network(heading="Lab4 Task 1 - Laboratory state space (all available actions)",
                  bgcolor="#242020", font_color="white", height="750px", width="100%",
                  directed=True, cdn_resources="in_line")
    # directed=True -> arrows, so A->B and B->A are separate edges with separate labels
    # cdn_resources="in_line" -> the JavaScript is put inside the HTML file (works offline)
    colors = {FREE: "white", DRONE: "white", TARGET: "green", START: "gold"}
    # drones are drawn white on purpose: the robot doesn't know where they are
    for s in labGraph.origin:                         # every state (non-wall cell)
        x, y = labGraph.getLocation(s)                # its grid position
        net.add_node(intTupleTostr(s), label=intTupleTostr(s), x=x * 2, y=y * 2,
                     color=colors[int(maze[s])], size=12, title=intTupleTostr(s))   # add the node
    for s, acts in labGraph.origin.items():           # every state and its actions
        for a, s2 in acts.items():                    # every available action and where it leads
            net.add_edge(intTupleTostr(s), intTupleTostr(s2), label=f"{a}:{ACTION_NAMES[a]}",
                         arrows="to", smooth={"type": "curvedCW", "roundness": 0.25},
                         font={"size": 9, "color": "white", "strokeWidth": 0})
            # one arrow s -> s2 labelled e.g. "2:Right"; curved so the reverse arrow is visible too
    net.toggle_physics(False)                         # keep nodes where we put them (no bouncing)
    # write as UTF-8 ourselves: pyvis' write_html uses the system encoding,
    # which fails on Windows (cp1252) with UnicodeEncodeError
    html = net.generate_html(notebook=False)          # build the HTML text
    with open(filename, "w", encoding="utf-8") as f:  # open the file as UTF-8
        f.write(html)                                 # save it
    return net


def decisionGraphNetwork(decision_graph, start, target, locations, filename="labDecisionGraph.html"):
    """pyvis picture of the compressed graph (start, target, junctions)."""
    from pyvis.network import Network
    net = Network(heading="Lab4 Task 1 - Decision graph (start, target, junctions)",
                  bgcolor="#242020", font_color="white", height="750px", width="100%",
                  directed=True, cdn_resources="in_line")   # same settings as above
    for s in decision_graph:                          # every key node
        color = "gold" if s == start else "green" if s == target else "violet"   # start / target / junction
        x, y = locations[s]                           # grid position
        net.add_node(intTupleTostr(s), label=intTupleTostr(s), x=x * 2, y=y * 2, color=color, size=14)
    for a, nbrs in decision_graph.items():            # every key node and its corridors
        for b, e in nbrs.items():                     # corridor a -> b with its info e
            net.add_edge(intTupleTostr(a), intTupleTostr(b),
                         label=f"steps {e['steps']}, cost {e['cost']}",          # shown on the arrow
                         title=" ".join(ACTION_NAMES[x] for x in e["actions"]),  # shown on mouse hover
                         arrows="to", smooth={"type": "curvedCW", "roundness": 0.25},
                         font={"size": 9, "color": "white", "strokeWidth": 0})
    net.toggle_physics(False)
    html = net.generate_html(notebook=False)          # same UTF-8 saving as above
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return net
