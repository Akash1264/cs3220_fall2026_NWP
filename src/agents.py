# for the Assignment3

from src.PS_agentPrograms import *
from src.mazeProblemSolvingAgentSMARTClass import MazeProblemSolvingAgentSMART



from src.vacuumProblemSolvingAgentSMARTClass import VacuumProblemSolvingAgentSMART
#from vacuumProblemSolvingAgentShowClass import VacuumProblemSolvingAgentDraw
from src.navProblemSolvingAgentClass import navProblemSolvingAgent


def ProblemSolvingMazeAgentBFS(initState,mazeWorldGraph,goalState):
    return MazeProblemSolvingAgentSMART(initState,mazeWorldGraph,goalState,BestFirstSearchAgentProgram())


def ProblemSolvingVacuumAgentBFS(initState,vacuumWorldGraph,goalState):
    return VacuumProblemSolvingAgentSMART(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgram())

 
def ProblemSolvingNavAgentBFS(initState,WorldGraph,goalState):
    return navProblemSolvingAgent(initState,WorldGraph,goalState,BestFirstSearchAgentProgram())

# def ProblemSolvingVacuumAgentBFSwithShow(initState,vacuumWorldGraph,goalState):
#     return VacuumProblemSolvingAgentDraw(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgramForShow())

# ---- Lab4 tasks: Rescue Robot agents (added for Task 2) ----
from src.rescueRobotAgentClass import RescueRobotAgent    # the Rescue Robot class

def RescueRobotAgentUCS(initState, labGraph, goalState, name="UCS-Robot"):
    return RescueRobotAgent(name, initState, labGraph, goalState, UniformCostSearchAgentProgram())
    # a Rescue Robot whose search program is Uniform-Cost Search

def RescueRobotAgentIDS(initState, labGraph, goalState, name="IDS-Robot"):
    return RescueRobotAgent(name, initState, labGraph, goalState, IDSearchAgentProgram())
    # a Rescue Robot whose search program is Iterative Deepening Search
