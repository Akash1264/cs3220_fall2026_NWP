# EXPLAINED COPY of src/droneClass.py - code identical to the real file.
import random                                         # Python's random numbers
from src.thingClass import Thing                      # instructor's base class for objects in an environment


class SecurityDrone(Thing):                           # a drone IS a Thing (as the assignment requires)
    """An enemy security drone placed in a lab cell."""
    def __init__(self, location, n_nodes, rng=None):  # location = (row, col); n_nodes = graph size
        rng = rng or random                           # use the given random generator, or the default one
        self.location = location                      # where the drone sits
        self.attack_power = round(rng.uniform(0.10 * n_nodes, 0.40 * n_nodes), 2)
        # random real number between 10% and 40% of the number of nodes, rounded to 2 decimals
        # e.g. 37 nodes -> between 3.7 and 14.8
        self.discovered_by = []                       # names of robots that have run into this drone

    def __repr__(self):                               # how the drone prints, e.g. in a list
        return f"<SecurityDrone at {self.location}, attack={self.attack_power}>"


def makeDrones(drone_cells, n_nodes, seed=None):      # create one drone for each drone cell
    rng = random.Random(seed)                         # own generator: same seed -> same attack powers
    return [SecurityDrone(cell, n_nodes, rng) for cell in drone_cells]   # list of drones
