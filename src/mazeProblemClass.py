
from src.problemClass import Problem

class MazeProblem(Problem):

    '''
    The state space is stored as nested dictionaries
    G={state1:{action1:state2, action2: state N..},
       .....}

    '''
    def __init__(self, initial, goal, graph):
      super().__init__(initial, goal)
      self.graph = graph#The state space 

    def actions(self, A):
      return list(self.graph.origin[A].keys())
      #return list(self.graph.get(A).keys())

    

    def result(self, state, action):
      print(1)
      #A transition model
      return self.graph.origin.get(state).get(action)
      #return self.graph.get(state).get(action)

    def path_cost(self, cost_so_far, A, action, B):
      #An action cost function
      #return cost_so_far + self.graph.graph_dict.get(A, B)
      print(A,B)
      print(self.graph.graph_dict.get(A).get(B))
      return cost_so_far + self.graph.graph_dict.get(A).get(B)