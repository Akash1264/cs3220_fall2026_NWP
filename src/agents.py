# for the Assignment3

from src.PS_agentPrograms import *
from src.vacuumProblemSolvingAgentSMARTClass import VacuumProblemSolvingAgentSMART
#from vacuumProblemSolvingAgentShowClass import VacuumProblemSolvingAgentDraw
from src.navProblemSolvingAgentClass import navProblemSolvingAgent

def ProblemSolvingVacuumAgentBFS(initState,vacuumWorldGraph,goalState):
    return VacuumProblemSolvingAgentSMART(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgram())

 
def ProblemSolvingNavAgentBFS(initState,WorldGraph,goalState):
    return navProblemSolvingAgent(initState,WorldGraph,goalState,BestFirstSearchAgentProgram())

# def ProblemSolvingVacuumAgentBFSwithShow(initState,vacuumWorldGraph,goalState):
#     return VacuumProblemSolvingAgentDraw(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgramForShow())