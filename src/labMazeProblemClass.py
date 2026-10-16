# EXPLAINED COPY of src/labMazeProblemClass.py - code identical to the real file.
from src.problemClass import Problem                  # instructor's abstract Problem class
from src.labMazeData import ACTION_COSTS              # action cost table


class LabMazeProblem(Problem):                        # the search problem the robots solve
    """Search problem for the Rescue Robot.

    State      : (row, col) of the robot
    Actions    : 0=Left, 1=Up, 2=Right, 3=Down (only the legal ones per state)
    Transition : graph.origin[state][action]
    Path cost  : sum of action costs + attack power of every drone the agent already knows about
    """
    def __init__(self, initial, goal, graph, known_drones=None):
        super().__init__(initial, goal)               # Problem stores self.initial and self.goal
        self.graph = graph                            # labMazeGraph instance (the state space)
        self.known_drones = known_drones or {}        # {cell: attack_power} the robot has met so far

    def actions(self, state):                         # ACTIONS(s)
        return list(self.graph.origin[state].keys())  # legal actions = keys of the transition model

    def result(self, state, action):                  # RESULT(s, a) - the transition model
        return self.graph.origin[state][action]       # look up where the action leads

    def path_cost(self, cost_so_far, A, action, B):   # cost of reaching B from A with `action`
        return cost_so_far + ACTION_COSTS[action] + self.known_drones.get(B, 0)
        # old cost + action cost + (attack power if B holds a drone we know about, else 0)
        # -> UCS avoids drones it has already met; unknown drones cost nothing in the plan

    # goal_test(state) is inherited from Problem: returns state == self.goal
