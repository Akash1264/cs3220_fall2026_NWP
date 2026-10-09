import collections

from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.graphProblemClass import GraphProblem

class navProblemSolvingAgent(SimpleProblemSolvingAgentProgram):
  def __init__(self, initial_state=None, dataGraph=None, goal=None, program=None):
    super().__init__(initial_state)
    self.dataGraph=dataGraph
    self.goal=goal
    
    self.performance=len(dataGraph.nodes())
    

    if program is None or not isinstance(program, collections.abc.Callable):
      print("Can't find a valid program for {}, falling back to default.".format(self.__class__.__name__))

      def program(percept):
        return eval(input('Percept={}; action? '.format(percept)))

    self.program = program


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
    problem = GraphProblem(state,goal,self.dataGraph)
    return problem  

  def search(self, problem):
    seq = self.program(problem)
    solution=self.actions_path(seq.path())
    print("Solution (a sequence of actions) from the initial state to a goal: {}".format(solution))
    return solution
  
  def actions_path(self, p):
    acts=[]
    for n in p:
      acts.append(n.action)
    return acts[1:]

  def run(self):
    print("goal list:", self.goal)
    if isinstance(self.goal, list) and len(self.goal)>1:
      percept=self.state
      while len(self.goal)>0:
        current_goal=self.goal[0]
        print("current percept:", percept)
        print("current goal:", current_goal)
        """Formulate a goal and problem, then search for a sequence of actions to solve it."""
        #4-phase problem-solving process
        self.state = self.update_state(self.state, percept)
        goal = current_goal
        problem = self.formulate_problem(self.state, goal)
        self.seq.append (self.search(problem))
        percept=current_goal
        self.goal.remove(goal)
        print("goal list:", self.goal)
      if not self.seq:
                return None
      return self.seq
    else:
      print ("I have the only goal = {}". format(self.goal))
      return super().__call__(self.state)
