# EXPLAINED COPY of src/labMazeGraphClass.py - code identical to the real file.
from src.maze2026GraphClass import mazeGraph          # the instructor's maze graph class (we extend it)
from src.labMazeData import ACTION_COSTS              # cost of each action: Left 2, Up 4, Right 2, Down 1


class labMazeGraph(mazeGraph):                        # our graph = instructor's mazeGraph + action costs
    """State-space graph of the laboratory.

    origin     -> the transition model {state: {action: next_state}}
    graph_dict -> {state: {next_state: action_cost}}  (directed, costs from ACTION_COSTS)
    Every non-wall cell is a node, even an isolated one.
    """
    # __init__ is inherited from mazeGraph: it saves the transition model in self.origin,
    # creates an empty self.graph_dict, calls make_graph (below) and saves the locations.

    def make_graph(self, graph_dict):                 # overrides the instructor's version
        for a in graph_dict.keys():                   # every state in the transition model
            self.graph_dict.setdefault(a, {})         # make sure the state is a node even with no exits
            for (act, b) in graph_dict[a].items():    # every (action, next state) from state a
                self.connect(a, b, ACTION_COSTS[act]) # edge a -> b weighted by the action's cost
                                                      # (instructor's version always used 1)
