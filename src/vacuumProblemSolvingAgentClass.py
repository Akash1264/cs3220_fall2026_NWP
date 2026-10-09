from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.vacuumProblemClass import VacuumProblem

class VacuumProblemSolvingAgent(SimpleProblemSolvingAgentProgram):
  def __init__(self, initial_state=None, dataGraph=None, goal=None):
    super().__init__(initial_state)
    self.dataGraph=dataGraph #instance of Vacuum ProblemClass 
    self.goal=goal
    
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
    #instance of Vacuum ProblemClass
    problem = VacuumProblem(state,goal,self.dataGraph)
    return problem  

  def search(self, problem):
    pass
