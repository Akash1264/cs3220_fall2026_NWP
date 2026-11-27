"""
CSPS.py
-------
Factory functions / classes that build concrete CSP problems.

  MapColoringCSP      -> original tutorial example (Australia map colouring)
  DinnerCSP           -> [Lab7 added] Task 1, Dinner Accommodation Problem
  AsteriskSudokuCSP   -> [Lab7 added] Task 2, Asterisk Sudoku (from Assignment 6)
"""

from src.CSPclass import CSP
from src.utils import *


# =============================================================================
# Tutorial example (unchanged)
# =============================================================================

def MapColoringCSP(colors, neighbors):
    """Make a CSP for the problem of coloring a map with different colors
    for any two adjacent regions. Arguments are a list of colors, and a
    dict of {region: [neighbor,...]} entries. This dict may also be
    specified as a string of the form defined by parse_neighbors."""
    if isinstance(neighbors, str):
        neighbors = parse_neighbors(neighbors)
    return CSP(list(neighbors.keys()), UniversalDict(colors), neighbors, different_values_constraint)


# =============================================================================
# [Lab7 added] TASK 1 - The Dinner Accommodation Problem
# =============================================================================
#
# Table layout (from the task picture), chairs numbered clockwise:
#
#                 [1]
#          +-------------+
#      [6] |             | [2]
#          |    TABLE    |
#      [5] |             | [3]
#          +-------------+
#                 [4]
#
# The 6 chairs form a RING: 1-2-3-4-5-6-1. Two chairs are "next to each
# other" when they are consecutive on this ring.
#
# CSP formulation
#   Variables   : the 5 colleagues  A, B, C, D, E
#   Domains     : the chairs        {1, 2, 3, 4, 5, 6}   (same for everybody)
#   Constraints :
#     (1) AllDifferent - two people cannot sit on the same chair
#         -> a binary "different chairs" constraint between EVERY pair
#     (2) "Not next to each other" for the 3 conflicting pairs:
#           A despises B            -> A, B not adjacent
#           B argues with E         -> B, E not adjacent
#           C is B's manager        -> B, C not adjacent
#   Neighbours  : because of AllDifferent every person is a neighbour of every
#                 other person (complete graph K5). The pairs A-B, B-E, B-C
#                 carry an EXTRA "not adjacent" constraint.
# -----------------------------------------------------------------------------

DINNER_PEOPLE = ['A', 'B', 'C', 'D', 'E']
DINNER_CHAIRS = [1, 2, 3, 4, 5, 6]

# Pairs that must not sit next to each other (+ the reason, used for labels)
DINNER_CONFLICTS = {
    frozenset(('A', 'B')): 'A despises B',
    frozenset(('B', 'E')): 'B argues with E',
    frozenset(('B', 'C')): 'C is B\'s manager',
}


def chairs_adjacent(c1, c2, n_chairs=6):
    """True if chairs c1 and c2 are next to each other on a round table
    with n_chairs seats (chair n is next to chair 1, so we use modulo)."""
    return (c1 - c2) % n_chairs in (1, n_chairs - 1)


class DinnerCSP(CSP):
    """[Lab7 added] Task 1 CSP, derived from the CSP class of the tutorial.

    Only two things are added on top of CSP:
      * the constraint function (dinner_constraint)
      * num_constraints(X, Y) - how many constraints connect X and Y,
        used by the Degree heuristic in Task 8.
    """

    def __init__(self, people=DINNER_PEOPLE, chairs=DINNER_CHAIRS,
                 conflicts=DINNER_CONFLICTS):
        self.chairs = list(chairs)
        self.conflicts = conflicts

        # Every person gets the same domain (all chairs) -> UniversalDict
        domains = UniversalDict(list(chairs))

        # AllDifferent links every person with every other person
        neighbors = {p: [q for q in people if q != p] for p in people}

        # CSPBasic(variables, domains, neighbors, constraints)
        super().__init__(list(people), domains, neighbors, self.dinner_constraint)

    def dinner_constraint(self, A, a, B, b):
        """f(A, a, B, b): True when person A on chair a and person B on
        chair b are compatible."""
        if a == b:                                    # (1) same chair -> not allowed
            return False
        if frozenset((A, B)) in self.conflicts:       # (2) enemies ...
            return not chairs_adjacent(a, b, len(self.chairs))   # ... must not be adjacent
        return True                                   # anybody else: fine

    def num_constraints(self, X, Y):
        """Number of separate constraints between X and Y:
        1 (different chairs) + 1 more if X and Y must also not be adjacent."""
        if Y not in self.neighbors[X]:
            return 0
        return 1 + (frozenset((X, Y)) in self.conflicts)

    def display(self, assignment):
        """Print the table with who sits where (empty chair = '--')."""
        seat = {c: '--' for c in self.chairs}
        for person, chair in assignment.items():
            seat[chair] = person
        print(f"            [1:{seat[1]:>2}]")
        print(f"   [6:{seat[6]:>2}]              [2:{seat[2]:>2}]")
        print(f"   [5:{seat[5]:>2}]              [3:{seat[3]:>2}]")
        print(f"            [4:{seat[4]:>2}]")


def check_dinner_solution(csp, assignment):
    """Return True if `assignment` satisfies every constraint of the dinner CSP
    (used to double-check the solutions found by every heuristic)."""
    people = list(assignment)
    return (len(assignment) == len(csp.variables) and
            all(csp.constraints(X, assignment[X], Y, assignment[Y])
                for i, X in enumerate(people) for Y in people[i + 1:]))


# =============================================================================
# [Lab7 added] TASK 2 - Asterisk Sudoku (puzzle from Assignment 6 / Lab 6)
# =============================================================================
#
# A normal 9x9 Sudoku (rows, columns, 3x3 boxes must contain 1..9 once)
# plus ONE EXTRA unit: the 9 shaded "asterisk" cells must also contain 1..9.
#
#   Variables   : 81 cells named A1 .. I9 (row letter + column number)
#   Domains     : given cell -> [its digit]; empty cell -> [1..9]
#   Neighbours  : cells sharing a row, column, box or the asterisk
#   Constraint  : neighbours must have different values
# -----------------------------------------------------------------------------

SUDOKU_ROWS = 'ABCDEFGHI'
SUDOKU_COLS = '123456789'

# The 9 asterisk cells (shaded in the Assignment 6 picture)
ASTERISK_CELLS = ['B5', 'C3', 'C7', 'E2', 'E5', 'E8', 'G3', 'G7', 'H5']

# Givens of the Assignment 6 puzzle, 0 = empty cell
ASTERISK_PUZZLE = [
    [0, 1, 0, 0, 0, 0, 0, 6, 0],
    [3, 0, 9, 0, 0, 0, 1, 0, 5],
    [0, 8, 0, 3, 0, 5, 0, 7, 0],
    [0, 0, 2, 0, 7, 0, 8, 0, 0],
    [0, 0, 0, 6, 0, 8, 0, 0, 0],
    [0, 0, 8, 0, 9, 0, 2, 0, 0],
    [0, 2, 0, 4, 0, 1, 0, 9, 0],
    [9, 0, 4, 0, 0, 0, 6, 0, 1],
    [0, 3, 0, 0, 0, 0, 0, 8, 0],
]


def sudoku_cell(r, c):
    """(row index 0..8, col index 0..8) -> cell name like 'A1'."""
    return SUDOKU_ROWS[r] + SUDOKU_COLS[c]


def sudoku_units(asterisk=ASTERISK_CELLS):
    """Every 'unit' (group of 9 cells that must all differ), grouped by type:
    {'row': [...], 'col': [...], 'box': [...], 'asterisk': [...]}."""
    rows = [[sudoku_cell(r, c) for c in range(9)] for r in range(9)]
    cols = [[sudoku_cell(r, c) for r in range(9)] for c in range(9)]
    boxes = [[sudoku_cell(r, c)
              for r in range(br, br + 3) for c in range(bc, bc + 3)]
             for br in (0, 3, 6) for bc in (0, 3, 6)]
    units = {"row": rows, "col": cols, "box": boxes}
    if asterisk:
        units["asterisk"] = [list(asterisk)]
    return units


def AsteriskSudokuCSP(grid=ASTERISK_PUZZLE, asterisk=ASTERISK_CELLS):
    """Build the Asterisk Sudoku CSP (a CSP object).
    grid     : 9x9 list of lists, 0 = empty cell
    asterisk : the 9 shaded cells (pass [] for a classic Sudoku)"""
    # Variables in reading order A1, A2, ..., I9
    variables = [sudoku_cell(r, c) for r in range(9) for c in range(9)]

    # Domains: a given cell can only keep its given value
    domains = {}
    for r in range(9):
        for c in range(9):
            v = grid[r][c]
            domains[sudoku_cell(r, c)] = [v] if v else list(range(1, 10))

    # Neighbours: union of all units the cell is in (set -> no duplicates)
    neighbors = {v: set() for v in variables}
    for unit_list in sudoku_units(asterisk).values():
        for unit in unit_list:
            for a in unit:
                neighbors[a].update(b for b in unit if b != a)
    neighbors = {v: sorted(n) for v, n in neighbors.items()}   # deterministic order

    return CSP(variables, domains, neighbors, different_values_constraint)


def check_sudoku_solution(assignment, asterisk=ASTERISK_CELLS):
    """True if every unit (rows, cols, boxes, asterisk) contains 1..9 exactly once."""
    return all(sorted(assignment[c] for c in unit) == list(range(1, 10))
               for unit_list in sudoku_units(asterisk).values()
               for unit in unit_list)


def print_sudoku(values, asterisk=ASTERISK_CELLS):
    """Pretty-print a Sudoku. `values` maps cell -> int, or cell -> list
    (a domain; single-value domains print as the digit, others as '.')."""
    for r in range(9):
        if r in (3, 6):
            print("------+-------+------")
        line = []
        for c in range(9):
            if c in (3, 6):
                line.append("|")
            v = values.get(sudoku_cell(r, c), 0)
            if isinstance(v, (list, tuple, set)):
                v = list(v)[0] if len(v) == 1 else 0
            line.append(str(v) if v else ".")
        print(" ".join(line))
