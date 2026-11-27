# from src.agentPrograms import *
# from src.agentClass import Agent

# from src.rules import vacuumRules
# from src.rules import actionList
# from src.rules import table




# '''Randomly choose one of the actions from the vacuum environment'''
# def RandomVacuumAgent():
#     return Agent(RandomAgentProgram(actionList))


# def TableDrivenVacuumAgent():
#      return Agent(TableDrivenAgentProgram(table))
 
 
# def ReflexAgent() :
#   return Agent(ReflexAgentProgram(vacuumRules,interpret_input,rule_match))


# def ReflexAgentA2pro():
#     pass
#     #your code here
  

# for the Assignment3

import math

from src.PS_agentPrograms import A_StarSearchAgentProgram
from src.mazeProblemSolvingAgentSMARTClass import MazeProblemSolvingAgentSMART
#from vacuumProblemSolvingAgentShowClass import VacuumProblemSolvingAgentDraw
#from src.navProblemSolvingAgentClass import navProblemSolvingAgent

def ProblemSolvingMazeAgentAstar(initState,mazeWorldGraph,goalState):
    #Astar_AP_EvcDist=A_StarSearchAgentProgram(math.dist)
    #return MazeProblemSolvingAgentSMART(initState,mazeWorldGraph,goalState,Astar_AP_EvcDist)
    return MazeProblemSolvingAgentSMART(initState,mazeWorldGraph,goalState,A_StarSearchAgentProgram(math.dist))


# def ProblemSolvingMazeAgentBFS(initState,mazeWorldGraph,goalState):
#     return MazeProblemSolvingAgentSMART(initState,mazeWorldGraph,goalState,BestFirstSearchAgentProgram())

 
# def ProblemSolvingNavAgentBFS(initState,WorldGraph,goalState):
#     return navProblemSolvingAgent(initState,WorldGraph,goalState,BestFirstSearchAgentProgram())

# def ProblemSolvingVacuumAgentBFSwithShow(initState,vacuumWorldGraph,goalState):
#     return VacuumProblemSolvingAgentDraw(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgramForShow())