"""
algorithms.py
-------------
Search / inference algorithms for CSPs used in Lab 7.

What is in this file:
  1. AC3, revise, back_revise      -> constraint propagation (arc consistency)
  2. Variable-ordering heuristics  -> first_unassigned_variable (default),
                                      mrv, mrv_degree                [Lab7 added]
  3. Value-ordering heuristics     -> unordered_domain_values (default),
                                      lcv                            [Lab7 added]
  4. backtracking_search           -> the backtracking search itself
                                      (now also counts explored nodes and can
                                       record a step-by-step trace)  [Lab7 changed]

Everything marked [Lab7 added] / [Lab7 changed] is new for this lab.
The original behaviour of every function is unchanged when it is called the
same way as in the tutorial (all new parameters have backward-compatible
defaults).
"""

from queue import Queue

from src.utils import first, count


# =============================================================================
# 1. AC-3 (constraint propagation)
# =============================================================================

def AC3(csp, verbose=True):
    """Make the whole CSP arc-consistent.

    For every arc (Xi, Xj) it removes values from Xi's domain that have no
    supporting value in Xj's domain. Pruned domains are kept in
    csp.curr_domains (the original csp.domains is never touched).

    Returns (consistent, checks):
        consistent -> False if some domain became empty (no solution)
        checks     -> how many constraint checks were made

    [Lab7 changed] `verbose` added (default True = original tutorial output).
    Pass verbose=False for big problems such as the 81-cell Sudoku, otherwise
    thousands of lines are printed.
    """
    queue = Queue()

    # Put every arc (Xi -> Xk) of the constraint graph in the queue
    if verbose:
        print(f"Initial queue:")
    for Xi in csp.variables:
        for Xk in csp.neighbors[Xi]:
            queue.put((Xi, Xk))
            if verbose:
                print((Xi, Xk), end=" ")
        if verbose:
            print()

    # curr_domains is created here (a copy of the domains we are allowed to prune)
    csp.support_pruning()
    checks = 0
    while list(queue.queue):
        (Xi, Xj) = queue.get()
        revised, checks = revise(csp, Xi, Xj, checks, verbose)
        if revised:
            # If Xi lost all its values, the CSP cannot be solved
            if not csp.curr_domains[Xi]:
                return False, checks  # CSP is inconsistent
            # Xi changed -> every arc pointing INTO Xi must be re-checked
            for Xk in csp.neighbors[Xi]:
                if Xk != Xj:
                    queue.put((Xk, Xi))
        if verbose:
            print(f"Queue: {list(queue.queue)}")

    return True, checks  # CSP is satisfiable (arc consistent)


def revise(csp, Xi, Xj, checks=0, verbose=True):
    """Remove every value x of Xi that has NO value y in Xj with
    constraints(Xi, x, Xj, y) == True. Return (revised?, checks).

    [Lab7 changed] `verbose` added (default True = original output)."""
    revised = False
    if verbose:
        print(f'Arc {(Xi, Xj)} is cheking')
    for x in csp.curr_domains[Xi][:]:      # iterate over a copy because we prune
        # Assume x is in conflict until we find one supporting y
        conflict = True
        for y in csp.curr_domains[Xj]:
            if csp.constraints(Xi, x, Xj, y):
                conflict = False
            checks += 1
            if not conflict:
                break                      # support found -> keep x
        if conflict:
            csp.prune(Xi, x)               # no support -> delete x
            if verbose:
                print(f'The val {x} was deleted from {Xi} domain')
            revised = True
    return revised, checks


def back_revise(csp, Xi, Xj, checks=0):
    """(Original tutorial helper, unchanged) Prunes values from Xj that
    conflict with values of Xi. Not used by the Lab 7 tasks."""
    revised = False
    for x in csp.curr_domains[Xi][:]:
        conflict = False
        for y in csp.curr_domains[Xj]:
            conflict = False
            if csp.constraints(Xi, x, Xj, y) == False:
                conflict = True
            checks += 1
            if conflict:
                csp.prune(Xj, y)
                print(f'The val {y} was deleted from {Xj} domain')
                revised = True
    return revised, checks


# =============================================================================
# 2. Variable ordering heuristics  (which variable do we assign next?)
# =============================================================================

def first_unassigned_variable(assignment, csp):
    """The default variable order: simply the first unassigned variable in
    csp.variables (no intelligence at all)."""
    return first([var for var in csp.variables if var not in assignment])


def num_legal_values(csp, var, assignment):
    """[Lab7 added] How many values of `var` are still legal, i.e. do NOT
    conflict with the variables that are already assigned.

    This is what 'remaining values' means for MRV when we do not use forward
    checking: we count the values that would pass the consistency test right now.
    """
    return count(csp.nconflicts(var, val, assignment) == 0
                 for val in csp.choices(var))


def mrv(assignment, csp):
    """[Lab7 added] Task 7 - Minimum Remaining Values heuristic.

    Pick the unassigned variable with the FEWEST legal values left
    ("fail-first": the most constrained variable is the one most likely to
    fail, so we try it early and discover dead ends sooner).

    Ties are broken by the order of csp.variables (min() keeps the first one).
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    return min(unassigned, key=lambda var: num_legal_values(csp, var, assignment))


def degree(csp, var, assignment):
    """[Lab7 added] Degree of `var` = number of constraints `var` has with
    OTHER UNASSIGNED variables.

    If the CSP defines `num_constraints(X, Y)` (how many separate constraints
    exist between X and Y), we use it; otherwise every neighbour counts as 1.
    """
    weight = getattr(csp, 'num_constraints', lambda X, Y: 1)
    return sum(weight(var, n) for n in csp.neighbors[var] if n not in assignment)


def mrv_degree(assignment, csp):
    """[Lab7 added] Task 8 - MRV with the Degree heuristic as tie-breaker.

    1. Smallest number of legal values  (MRV)          -> sort key #1 (ascending)
    2. Largest number of constraints on
       other unassigned variables (Degree)              -> sort key #2 (descending,
                                                           so we use the minus sign)
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    return min(unassigned,
               key=lambda var: (num_legal_values(csp, var, assignment),
                                -degree(csp, var, assignment)))


# =============================================================================
# 3. Value ordering heuristics  (in which order do we try the values?)
# =============================================================================

def unordered_domain_values(var, assignment, csp):
    """The default value order: the domain exactly as it is stored."""
    return csp.choices(var)


def lcv(var, assignment, csp):
    """[Lab7 added] Task 9 - Least Constraining Value heuristic.

    For every value `val` of `var` we count how many values it would REMOVE
    from the neighbouring UNASSIGNED variables. We only count neighbour values
    y that are STILL LEGAL right now (no conflict with the current assignment),
    because a value that is already impossible cannot be "removed" again.
    A legal y is removed if constraints(var, val, n, y) is False.

    Values are returned sorted from 'removes the fewest' to 'removes the most',
    so we try the value that leaves the most freedom to the others first.
    Values that already conflict with the assignment are put at the end.
    Python's sort is stable, so ties keep the original domain order.
    """
    def ruled_out(val):
        return sum(1
                   for n in csp.neighbors[var] if n not in assignment
                   for y in csp.choices(n)
                   if csp.nconflicts(n, y, assignment) == 0      # y still legal
                   and not csp.constraints(var, val, n, y))       # ...but val kills it

    # Sort key: (is the value illegal right now?, how many options it removes)
    # -> legal values first, ordered by fewest removals; illegal values last
    #    (they will be rejected by the consistency check anyway).
    return sorted(csp.choices(var),
                  key=lambda val: (csp.nconflicts(var, val, assignment) > 0, ruled_out(val)))


# =============================================================================
# 4. Backtracking search
# =============================================================================

def backtracking_search(csp, select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values, trace=None,
                        trace_conflicts=True):
    """Depth-first search over partial assignments that backtracks as soon
    as a variable has no consistent value left.

    Parameters
    ----------
    select_unassigned_variable : variable-ordering function
                                 (first_unassigned_variable / mrv / mrv_degree)
    order_domain_values        : value-ordering function
                                 (unordered_domain_values / lcv)
    trace                      : [Lab7 added] optional list. If given, every
                                 step of the search is appended to it as a dict,
                                 so the Streamlit apps can replay the search.
    trace_conflicts            : [Lab7 added] also record rejected values
                                 ('conflict' steps). Set False for big problems.

    Statistics stored on the csp object after the search  [Lab7 added]:
        csp.nassigns       -> number of variable assignments (already existed,
                              incremented in CSP.assign)
        csp.nodes_explored -> number of search-tree nodes visited
                              (= number of calls to backtrack())
        csp.nbacktracks    -> number of times we had to undo an assignment
    """
    # [Lab7 added] counters kept in a dict so the inner function can update them
    stats = {'nodes': 0, 'backtracks': 0}

    def record(action, var=None, value=None):
        """[Lab7 added] Save one search step (only if a trace list was given).
        A step is a small tuple (action, var, value) so that even a search with
        hundreds of thousands of steps fits in memory. Use replay_trace() to
        rebuild the assignment at any step.
        action is one of: 'assign' | 'conflict' | 'backtrack' | 'solution' | 'failure'"""
        if trace is not None:
            if action == 'conflict' and not trace_conflicts:
                return
            trace.append((action, var, value))

    def backtrack(assignment):
        stats['nodes'] += 1                          # we are visiting a new node
        # Goal test: every variable has a value -> solution found
        if len(assignment) == len(csp.variables):
            record('solution')
            return assignment

        # Choose the next variable (heuristic decides)
        var = select_unassigned_variable(assignment, csp)
        # Try its values (heuristic decides the order)
        for value in order_domain_values(var, assignment, csp):
            if csp.nconflicts(var, value, assignment) == 0:
                # value is consistent with what is already assigned -> go deeper
                csp.assign(var, value, assignment)
                record('assign', var, value)
                result = backtrack(assignment)
                if result is not None:
                    return result
                # the subtree failed -> undo and try the next value
                stats['backtracks'] += 1
                csp.unassign(var, assignment)
                record('backtrack', var, value)
            else:
                # value violates a constraint with an assigned neighbour
                record('conflict', var, value)
            csp.unassign(var, assignment)
        return None                                  # no value worked -> fail

    result = backtrack({})
    if result is None:
        record('failure')

    # [Lab7 added] expose the statistics for the comparisons in Tasks 7-9
    csp.nodes_explored = stats['nodes']
    csp.nbacktracks = stats['backtracks']
    return result


def replay_trace(trace, upto):
    """[Lab7 added] Rebuild the partial assignment after the first `upto`
    steps of a trace produced by backtracking_search(..., trace=[...]).
    'assign' adds var=value, 'backtrack' removes var; the other actions do
    not change the assignment."""
    assignment = {}
    for action, var, value in trace[:upto]:
        if action == 'assign':
            assignment[var] = value
        elif action == 'backtrack':
            assignment.pop(var, None)
    return assignment
