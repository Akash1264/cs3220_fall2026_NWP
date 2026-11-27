from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.mazeProblemClass import MazeProblem

class MazeProblemSolvingAgent(SimpleProblemSolvingAgentProgram):
  def __init__(self, initial_state=None, dataGraph=None, goal=None):
    super().__init__(initial_state)
    self.dataGraph=dataGraph
    self.goal=goal
    #instance of Maze ProblemClass
    #self.problem=problem #a description of the states and actions necessary to reach the goal
    #self.goal = self.problem.goal#The agent adopts the goal

  def update_state(self, state, percept):
    return percept

  def formulate_goal(self, state):
    if self.goal is not None:
      return self.goal
    else:
      print("No goal! can't work!")
      return None

  #a description of the states and actions necessary to reach the goal
  def formulate_problem(self, state, goal):
    #instance of Maze ProblemClass
    problem = MazeProblem(state,goal,self.dataGraph)
    return problem  

  def search(self, problem):
    pass
