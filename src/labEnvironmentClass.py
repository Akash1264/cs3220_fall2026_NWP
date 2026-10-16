# EXPLAINED COPY of src/labEnvironmentClass.py - code identical to the real file.
from src.environmentClass import Environment          # instructor's base Environment
from src.droneClass import SecurityDrone              # to recognise drones
from src.labMazeData import ACTION_NAMES, ACTION_COSTS   # action names and costs


class LabEnvironment(Environment):                    # the hazardous laboratory
    """Walls/boundaries, move costs, drones (Defense Mode / capture), reaching the target."""
    def __init__(self, maze, labGraph, drones=()):
        super().__init__()                            # parent creates self.agents = []
        self.maze = maze                              # the NumPy grid
        self.status = labGraph                        # the state-space graph (same name as the tutorial env)
        self.things = list(drones)                    # non-agent objects in the lab = the drones

    def drone_at(self, location):                     # is there a drone in this cell?
        for t in self.things:                         # look through all things
            if isinstance(t, SecurityDrone) and t.location == location:
                return t                              # found -> return the drone
        return None                                   # no drone here

    def percept(self, agent):                         # what the agent senses
        return agent.state                            # only its own cell (it can't see drones)

    def add_thing(self, thing, location=None):        # put a drone or a robot into the lab
        if isinstance(thing, SecurityDrone):          # a drone:
            if location is not None:
                thing.location = location             # optionally move it
            self.things.append(thing)                 # add it to the things
            return
        super().add_thing(thing, location)            # a robot: parent calls thing(thing.state) -> the robot
                                                      # runs phases 1-3 and gets its plan, then is added to agents
        if thing in self.agents and thing.status == "no solution":
            thing.alive = False                       # no plan -> the robot can't do anything
        self.update_agent_alive(thing)                # in case it already starts on the target

    def is_agent_alive(self, agent):
        return agent.alive                            # still active?

    def update_agent_alive(self, agent):              # check whether a robot is finished
        if not agent.alive:                           # already finished -> nothing to do
            return
        if agent.energy <= 0:                         # battery empty
            agent.alive = False
            agent.status = "out of energy"
            print(f"{agent.name} ran out of energy at {agent.state}.")
        elif agent.state == agent.goal:               # standing on the target
            agent.alive = False                       # mission complete, it stops
            agent.status = "rescued"
            print(f"*** {agent.name} reached the Rescue Target {agent.goal} "
                  f"with energy {agent.energy:.2f} ***")

    def execute_action(self, agent, action):          # carry out ONE action of ONE robot
        if not self.is_agent_alive(agent):            # finished robots don't move
            return
        next_state = self.status.origin.get(agent.state, {}).get(action)
        # look up RESULT(state, action) in the transition model; None if not allowed
        if next_state is None:                        # wall or boundary
            print(f"{agent.name}: {ACTION_NAMES.get(action, action)} is blocked at {agent.state}.")
            agent.spend_energy(1)                     # bumping costs 1 energy
            agent.replan()                            # make a new plan
            self.update_agent_alive(agent)
            return

        agent.state = agent.update_state(agent.state, next_state)   # move the robot
        agent.spend_energy(ACTION_COSTS[action])      # pay the move cost (Left 2, Up 4, Right 2, Down 1)
        agent.steps += 1                              # count the move
        agent.path.append(next_state)                 # remember the path (for the picture)
        print(f"{agent.name}: {ACTION_NAMES[action]} -> {agent.state}, energy = {agent.energy:.2f}")

        drone = self.drone_at(next_state)             # did it walk into a drone?
        if drone is not None:
            if agent.name not in drone.discovered_by:
                drone.discovered_by.append(agent.name)   # note which robot found it
            agent.perceive_drone(drone)               # the drone becomes known to the agent
            defense = agent.energy                    # defensive capability = current energy
            if drone.attack_power >= 2 * defense:     # drone at least twice as strong?
                agent.alive = False                   # -> robot is captured and dies
                agent.status = "captured"
                print(f"!!! {agent.name} met a drone (attack {drone.attack_power}) at {next_state} "
                      f"with defense {defense:.2f} -> CAPTURED")
                return
            loss = 0.10 * agent.energy                # otherwise DEFENSE MODE costs 10% of current energy
            agent.spend_energy(loss)                  # energy update (part of the agent's state)
            agent.defense_activations += 1            # count it
            print(f"!!! {agent.name} met a drone (attack {drone.attack_power}) at {next_state}: "
                  f"Defense Mode ON, -{loss:.2f} energy -> {agent.energy:.2f}")
            self.update_agent_alive(agent)            # maybe the drone was on the target / energy hit 0
            if agent.alive:
                agent.replan()                        # new knowledge -> plan again
            return
        self.update_agent_alive(agent)                # normal move: check target / energy

    def step(self):                                   # one time step for ALL robots
        if self.is_done():                            # parent: True when no robot is alive
            print("There is no one here who could work...")
            return
        actions = []                                  # first collect one action per robot
        for agent in self.agents:
            if agent.alive and agent.seq:             # active and has a plan
                actions.append(agent.seq.pop(0))      # take the next action from its plan
            else:
                if agent.alive:                       # active but no plan left
                    agent.alive = False               # -> it stops
                    if agent.status != "rescued":
                        agent.status = "stuck"
                actions.append(None)                  # nothing to do for this robot
        for agent, action in zip(self.agents, actions):   # then execute them (both robots move in the same step)
            if action is not None:
                self.execute_action(agent, action)

    def run(self, steps=200):                         # run until everyone is finished (max 200 steps)
        for step in range(steps):
            if self.is_done():                        # all robots finished
                print(f"--- all agents finished after {step} steps ---")
                return
            print(f"step {step + 1}:")
            self.step()                               # advance one step
