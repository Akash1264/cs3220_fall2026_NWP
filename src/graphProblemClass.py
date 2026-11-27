from src.problemClass import Problem

class GraphProblem(Problem):

    """The problem of searching a graph from one node to another."""
    '''
    The state space is stored as nested dictionaries
    G={'node1':{'neighbor1_of_Node1':distance_from_Node1_to_neighbor1_of_Node1,..},
       .....}

    '''

    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal)
        self.graph = graph#The state space

    def actions(self, A):
        """The actions at a graph node are just its neighbors."""
        return list(self.graph.get(A).keys())

    def result(self, state, action):
      #A transition model
        """The result of going to a neighbor is just that neighbor."""
        return action

    def path_cost(self, cost_so_far, A, action, B):
      #An action cost function
        return cost_so_far + self.graph.get(A, B)