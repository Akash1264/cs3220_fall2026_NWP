import random
from src.locations import *

from src.Task1_YourRecipientsClasses import OfficeManager,Student,ITStaff
from src.catFriendlyHouse_membersClass import Milk, Sausage, Mouse, Dog

from src.agentClass import MouseAgent

'''An idea of Random Agent Program is to choose an action at random, ignoring all percepts'''
def RandomAgentProgram(actions):
   return lambda percept: random.choice(actions)

def TableDrivenAgentProgram(table):
    """
    This agent selects an action based on the percept sequence.
    To customize it, provide as table a dictionary of all 
    {percept_sequence:action} pairs.
    """
    percepts = []

    def program(percept):
        percepts.append(percept)
        #print(tuple(percepts))
        action = table.get(tuple(percepts))
        
        if action is None:
          print("Not such percept sequence in my table")

        return action

    return program
  
  
def ReflexAgentProgram(rules,interpret_input,rule_match):
  #This AP takes action based solely on the percept.
    
    def program(percept):
        state = interpret_input(percept)
        action = rule_match(state, rules)
        return action

    return program


def interpret_input(percept):
  loc, status = percept
  return status


def rule_match(state, rules):
  for key in rules:
    if state in key:
      return rules[key]




#The code below -> for Task1x of the Assignment



def interpret_input_A2pro(percept):
  loc, percepts = percept
  #print(percepts,loc, loc_D)
  status='Clear'
  if len(percepts)==0:
    if loc==loc_D:
      status='Last room'
      
  else:
    for p in percepts:
      if isinstance(p, OfficeManager):
        return 'Office manager'
      elif isinstance(p, ITStaff):
        return 'IT'
      elif isinstance(p, Student):
        return 'Student'
  print(status)
  return status

def rule_match_A2pro(state, rules):
  return rules[state]


def interpret_input_A3pro(percept):
  loc, status = percept
  if isinstance(status, list):
    for item in ['Sausage', 'Milk', 'Mouse']:
      if item in status:
        return item
  return status

def interpret_input_A4pro(percept):
  #for Cat-Agent & Mouse-RandomAgent
  loc, agents,things = percept
  percepts=agents+things
  print(percepts)
  status='Clear'     
  
  for p in percepts:
      if isinstance(p, MouseAgent):
        print("Oh! the Mouse is here")
        return 'Mouse'

  for p in percepts:
      if isinstance(p, Dog):
        print("Oh no! A Dog is here")
        return 'Dog'
      
  if status=='Clear':
    if loc==loc_D or loc==loc_A:
      status='Last room'


  print(f"Loc: {loc}, status: {status}")
  return status



  