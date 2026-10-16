# EXPLAINED COPY of src/rescueRobotAgentClass.py - code identical to the real file.
import collections                                    # for collections.abc.Callable (checks "is it a function?")
from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram   # instructor's 4-phase agent
from src.labMazeProblemClass import LabMazeProblem    # the search problem the robot builds
from src.labMazeData import ACTION_NAMES              # 0 -> "Left" etc., for printing plans


class RescueRobotAgent(SimpleProblemSolvingAgentProgram):   # our robot = the instructor's problem-solving agent
    """Problem-solving Rescue Robot.
    Agent state = position + energy + drones it has discovered (see robot_state).
    """
    def __init__(self, name, initial_state, dataGraph, goal, program):
        super().__init__(initial_state)               # parent sets self.state, self.seq=[], performance, alive=True
        if program is None or not isinstance(program, collections.abc.Callable):
            raise ValueError("RescueRobotAgent needs a search program")   # must be given UCS or IDS
        self.name = name                              # "UCS-Robot" or "IDS-Robot"
        self.dataGraph = dataGraph                    # the lab's state-space graph
        self.goal = goal                              # the rescue target cell
        self.program = program                        # the search algorithm (a function)

        self.energy = float(len(dataGraph.nodes()))   # battery starts at the number of graph nodes (37)
        self.performance = self.energy                # performance is kept equal to energy
        self.known_drones = {}                        # drones met so far: {cell: attack_power}
        self.path = [initial_state]                   # cells visited, starting with the start cell
        self.steps = 0                                # number of moves made
        self.defense_activations = 0                  # how many times Defense Mode was used
        self.replans = 0                              # how many times it searched again
        self.status = "planning"                      # later: moving / rescued / captured / out of energy ...
        self.search_log = []                          # statistics of every search (nodes expanded ...)

    def __repr__(self):                               # how the robot prints
        return f"<{self.name}>"

    # ---- agent state ------------------------------------------------------
    @property                                         # read like a variable: robot.robot_state
    def robot_state(self):                            # the full agent state the assignment asks for
        return {"position": self.state, "energy": round(self.energy, 2),
                "known_drones": dict(self.known_drones)}

    def spend_energy(self, amount):                   # lower the battery
        self.energy = max(0.0, self.energy - amount)  # subtract, but never go below 0
        self.performance = self.energy                # keep performance in sync

    def perceive_drone(self, drone):                  # the environment tells the robot "a drone is here"
        self.known_drones[drone.location] = drone.attack_power   # the drone becomes known

    # ---- 4 phases of the problem-solving agent ----------------------------
    # (the parent's __call__ runs: update_state -> formulate_goal -> formulate_problem -> search)
    def update_state(self, state, percept):           # new state from a percept
        return percept                                # the percept IS the new cell

    def formulate_goal(self, state):                  # PHASE 1: goal formulation
        if self.goal is None:
            print("No goal! can't work!")
        return self.goal                              # the only goal: the rescue target

    def formulate_problem(self, state, goal):         # PHASE 2: problem formulation
        return LabMazeProblem(state, goal, self.dataGraph, self.known_drones)
        # search problem from the current cell, including the drones known so far

    def search(self, problem):                        # PHASE 3: search
        node = self.program(problem)                  # run UCS or IDS -> goal Node or None
        stats = dict(getattr(self.program, "stats", {}))   # copy the search counters
        self.search_log.append({"from": problem.initial, **stats})   # keep them for the results table
        if node is None:                              # no path exists
            self.status = "no solution"
            print(f"{self.name}: no path from {problem.initial} to {problem.goal}")
            return []                                 # empty plan
        solution = node.solution()                    # follow parent links -> list of actions
        print(f"{self.name}: plan from {problem.initial} = {solution} "
              f"({' '.join(ACTION_NAMES[a] for a in solution)}), planned cost = {node.path_cost:g}, "
              f"nodes expanded = {stats.get('expanded')}")   # print the plan
        self.status = "moving"
        return solution                               # the parent stores this in self.seq
    # PHASE 4 (execution) is done by LabEnvironment.step(), which pops actions from self.seq

    def replan(self):                                 # search again from where the robot is now
        self.replans += 1                             # count it
        self.seq = self.search(self.formulate_problem(self.state, self.goal))   # new plan replaces old one
