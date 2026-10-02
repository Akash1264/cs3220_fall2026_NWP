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

import collections.abc #we need collections.abc which provides abstract base classes that can be used to test whether a class provides a particular interface

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

class CatAgent(Agent):

    def __init__(self, program=None):
        super().__init__(program)
        self.direction = True

    def changeDirection(self):
        self.direction = not self.direction

    def drink(self, food):
        from src.catFriendlyHouse_membersClass import Milk
        if not isinstance(food, Milk):
            print(f"The Cat can't drink {food}!")
            return False
        self.performance += food.energy
        return True

    def eat(self, food):
        from src.catFriendlyHouse_membersClass import Sausage
        if not isinstance(food, Sausage):
            print(f"The Cat can't eat {food}!")
            return False
        self.performance += food.energy
        return True

    def catch(self, mouse):
        from src.catFriendlyHouse_membersClass import Mouse
        if not isinstance(mouse, Mouse):
            print(f"The Cat can't catch {mouse}!")
            return False
        if self.performance < mouse.size * 10:
            return False
        self.performance += mouse.energy // 100
        return True


directions={
    True:'Left to Right',
    False:'Right to Left',
}

class proCatAgent(Agent):
    """Task 3 cat. direction: True = Left to Right, False = Right to Left."""

    def __init__(self, program=None, performance=50):
        super().__init__(program)
        self.direction = True
        self.performance = performance  # starting strength (env2 keeps it, doesn't reset to 0)

    def changeDirection(self):
        self.direction = not self.direction
        print(f"The Cat changed direction: {directions[self.direction]}")


class MouseAgent(Agent):
    """Task 3 mouse. Moves randomly; each move costs 1 performance.
    At performance <= 0 it can't move anymore but stays in its room (still catchable)."""

    def __init__(self, program=None, size=1):
        super().__init__(program)
        self.size = size
        self.performance = size * 5  # starting energy
        self.eaten = False
