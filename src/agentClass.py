#This subclass of a base Thing class represents an Agent
'''It has one required slot (attribute), .program, which reperesents Agent Program (the Core of Agent's logic).
Agent Program should hold a function that takes one argument, the Percept, and returns an action.'''

'''!!! Note that '.program' is a slot, not a method.
If it were a method, then the program could 'cheat' and look at aspects of the agent.
It's not supposed to do that: the program can only look at the percepts'''

'''
There is an optional slot, .performance, which is a number giving
the performance measure of the agent in its environment.'''
from src.thingClass import Thing

import collections #we need collections.abc which provides abstract base classes that can be used to test whether a class provides a particular interface

class Agent(Thing):

    def __init__(self, program=None):
        self.alive = True
        self.performance = 0
        self.location=None

        if program is None or not isinstance(program, collections.abc.Callable):
            print("Can't find a valid program for {}, falling back to default.".format(self.__class__.__name__))

            def program(percept):
                return eval(input('Percept={}; action? '.format(percept)))

        self.program = program