"""
EXPLAINED COPY of src/labMazeData.py
Every line has a comment saying what it does. The code is identical to the real file.

Task 1 - Hazardous Laboratory Maze: data generation, transition model and decision graph.
Cell encoding of the NumPy matrix:
    0 = free cell, 1 = wall / debris, 2 = security drone, 3 = rescue target, 4 = robot start
"""
import numpy as np                       # NumPy: the maze is stored as a 2D NumPy array
from collections import deque            # deque = fast queue, used by breadth-first search (BFS)

# ---- cell codes ----------------------------------------------------------
FREE, WALL, DRONE, TARGET, START = 0, 1, 2, 3, 4      # give each cell code a readable name
CELL_NAMES = {FREE: "free", WALL: "wall/debris", DRONE: "security drone",   # code -> text,
              TARGET: "rescue target", START: "start"}                      # used for printing

# ---- actions (encoded as integers 0-3) -----------------------------------
LEFT, UP, RIGHT, DOWN = 0, 1, 2, 3                    # the 4 actions as the assignment numbers them
ACTION_NAMES = {LEFT: "Left", UP: "Up", RIGHT: "Right", DOWN: "Down"}   # action number -> name
# (row delta, column delta)
ACTION_DELTAS = {LEFT: (0, -1), UP: (-1, 0), RIGHT: (0, 1), DOWN: (1, 0)}
#   how each action changes the position: Left = same row, column-1; Up = row-1; etc.
# action costs used by the UCS agent (and to drain the robot's energy)
ACTION_COSTS = {LEFT: 2, UP: 4, RIGHT: 2, DOWN: 1}    # cost table from Task 2


def makeLabMaze(n=7, wall_ratio=0.25, drone_ratio=0.10, seed=None,   # build a random n x n lab
                min_distance=None, max_tries=10_000):
    rng = np.random.default_rng(seed)                 # random generator; same seed -> same maze
    total = n * n                                     # number of cells (49 for 7x7)
    n_walls = round(total * wall_ratio)               # 25% of 49 = 12.25 -> 12 walls
    n_drones = round(total * drone_ratio)             # 10% of 49 = 4.9  -> 5 drones
    min_distance = n - 1 if min_distance is None else min_distance   # default: target >= 6 moves away

    for _ in range(max_tries):                        # keep trying until we get a good maze
        cells = rng.permutation(total)                # shuffle the numbers 0..48 (one per cell)
        maze = np.full((n, n), FREE, dtype=int)       # start with an all-free n x n grid
        for k in cells[:n_walls]:                     # the first 12 shuffled cells...
            maze[divmod(int(k), n)] = WALL            # ...become walls (divmod turns 17 into (2, 3))
        for k in cells[n_walls:n_walls + n_drones]:   # the next 5 shuffled cells...
            maze[divmod(int(k), n)] = DRONE           # ...become drones
        free = cells[n_walls + n_drones:]             # all remaining cells are free
        start = divmod(int(free[0]), n)               # first free cell = robot start (row, col)
        target = divmod(int(free[1]), n)              # second free cell = rescue target
        maze[start] = START                           # mark the start with code 4
        maze[target] = TARGET                         # mark the target with code 3

        d = bfsDistance(maze, start, target)          # shortest number of moves start -> target
        if d is not None and d >= min_distance:       # reachable AND not too close?
            return maze, start, target                # yes -> this maze is accepted
    raise RuntimeError("Could not generate a solvable maze - relax the parameters.")  # gave up


def bfsDistance(maze, start, target):                 # helper: shortest distance in moves
    n = maze.shape[0]                                 # grid size
    dist = {start: 0}                                 # distance from start to each visited cell
    q = deque([start])                                # BFS queue, begins with the start cell
    while q:                                          # while there are cells left to explore
        cur = q.popleft()                             # take the oldest cell in the queue
        if cur == target:                             # reached the target?
            return dist[cur]                          # return how many moves it took
        for di, dj in ACTION_DELTAS.values():         # try all 4 directions
            nxt = (cur[0] + di, cur[1] + dj)          # neighbour cell
            if 0 <= nxt[0] < n and 0 <= nxt[1] < n and maze[nxt] != WALL and nxt not in dist:
                # inside the grid, not a wall, and not visited yet
                dist[nxt] = dist[cur] + 1             # one move further than the current cell
                q.append(nxt)                         # explore it later
    return None                                       # queue empty and target never found


def findCells(maze, code):                            # list every cell that holds `code`
    return [tuple(int(v) for v in rc) for rc in np.argwhere(maze == code)]
    # np.argwhere gives [[r, c], ...]; we turn each into a plain (r, c) tuple


def availableActions(maze, state):                    # which actions are legal in this cell?
    n = maze.shape[0]                                 # grid size
    acts = []                                         # legal actions collected here
    for a, (di, dj) in ACTION_DELTAS.items():         # for every action and its movement
        ni, nj = state[0] + di, state[1] + dj         # where the action would take the robot
        if 0 <= ni < n and 0 <= nj < n and maze[ni, nj] != WALL:   # inside the lab and not a wall
            acts.append(a)                            # -> action is available
    return acts                                       # e.g. [2, 3] = Right and Down allowed


def makeLabTransitionModel(maze):                     # TRANSITION MODEL: RESULT(s, a)
    n = maze.shape[0]                                 # grid size
    tm = {}                                           # result: {state: {action: next_state}}
    for i in range(n):                                # every row
        for j in range(n):                            # every column
            if maze[i, j] == WALL:                    # walls are not states (robot never stands there)
                continue                              # skip them
            tm[(i, j)] = {}                           # this cell is a state; start its action dict
            for a in availableActions(maze, (i, j)):  # for each legal action from here
                di, dj = ACTION_DELTAS[a]             # its movement
                tm[(i, j)][a] = (i + di, j + dj)      # record: doing a in (i, j) leads to this cell
    return tm                                         # drone cells are included (robot can enter them)


def labStatesLocations(keyList, scale=60):            # screen (x, y) for each state when drawing
    return {s: (s[1] * scale, s[0] * scale) for s in keyList}
    # x = column * 60, y = row * 60 -> the graph is laid out like the grid


def makeDecisionGraph(tm, start, target):             # compact graph: start, target, junctions
    key_nodes = {s for s, acts in tm.items() if len(acts) >= 3} | {start, target}
    # junction = cell with 3+ exits (a real choice); always include start and target
    graph = {k: {} for k in key_nodes}                # empty edge dict for every key node
    for k in key_nodes:                               # from every key node...
        for a, nxt in tm[k].items():                  # ...try each way out of it
            acts, cells, cost = [a], [k], ACTION_COSTS[a]   # remember actions, cells and cost so far
            prev, cur, dead_end = k, nxt, False       # walk: came from k, now at nxt
            while cur not in key_nodes:               # keep walking until we hit another key node
                options = [(a2, s2) for a2, s2 in tm[cur].items() if s2 != prev]
                # ways to continue, excluding going back where we came from
                if len(options) != 1:                 # 0 options means a dead end
                    dead_end = True                   # remember that
                    break                             # stop walking this corridor
                a2, s2 = options[0]                   # the only way forward
                cells.append(cur)                     # add the current cell to the corridor
                acts.append(a2)                       # add the action taken
                cost += ACTION_COSTS[a2]              # add its cost
                prev, cur = cur, s2                   # step forward
            if dead_end or cur == k:                  # dead end, or corridor loops back to k
                continue                              # -> not a useful edge, skip it
            cells.append(cur)                         # include the key node we arrived at
            best = graph[k].get(cur)                  # is there already an edge k -> cur?
            if best is None or cost < best["cost"]:   # keep only the cheapest corridor
                graph[k][cur] = {"actions": acts, "cells": cells,
                                 "steps": len(acts), "cost": cost}   # store the edge
    return key_nodes, graph                           # directed: cost A->B can differ from B->A


def intTupleTostr(t):                                 # (2, 3) -> "2-3" (pyvis node ids are strings)
    return "-".join(str(item) for item in t)
