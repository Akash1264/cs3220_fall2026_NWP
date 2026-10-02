from src.agentPrograms import *
from src.agentClass import Agent, MouseAgent, proCatAgent, CatAgent

from src.rules import vacuumRules
from src.rules import actionList
from src.rules import table

#your code here
from src.rules import a2proRules
from src.rules import catRules, cat2Rules, mouseAgentLocations




'''Randomly choose one of the actions from the vacuum environment'''
def RandomVacuumAgent():
    return Agent(RandomAgentProgram(actionList))


def TableDrivenVacuumAgent():
     return Agent(TableDrivenAgentProgram(table))
 
 
def ReflexAgent() :
  return Agent(ReflexAgentProgram(vacuumRules,interpret_input,rule_match))


def ReflexAgentA2pro():
    return Agent(ReflexAgentProgram(a2proRules,interpret_input_A2pro,rule_match_A2pro))



def ReflexAgentA3pro():#cat Agent
    return CatAgent(ReflexAgentProgram(catRules,interpret_input_A3pro,rule_match_A2pro))


def RandomMouseAgent(): #for the Task3
    return MouseAgent(RandomAgentProgram(mouseAgentLocations))


def ReflexAgentA4pro():#cat Agent for mouse Agent - task3
    return proCatAgent(ReflexAgentProgram(cat2Rules,interpret_input_A4pro,rule_match))
    

