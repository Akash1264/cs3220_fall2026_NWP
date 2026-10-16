#How do we decide which node from the frontier to expand next?
from src.nodeClass import Node
from queue import PriorityQueue

nodeColors={
    "start":"red",
    "goal": "green",
    "frontier": "orange",
    "expanded":"pink"
}

def BestFirstSearchAgentProgram(f=None):
  #with BFS we choose a node, n, with minimum value of some evaluation function, f (n).
    
    def program(problem):

      node = Node(problem.initial)
      #node.color=nodeColors["start"]
      #print(node.state)
      frontier = PriorityQueue()
      frontier.put((1,node))
      #node.color=nodeColors["frontier"]
      reached = {problem.initial:node}

      while frontier:
        node = frontier.get()[1]
        #node.color=nodeColors["expanded"]
        print(node)

        if problem.goal_test(node.state):
          node.color=nodeColors["goal"]
          return node

        #reached.add(node.state)
        for child in node.expand(problem):
            if child.state not in reached or child.path_cost<reached[child.state].path_cost:
                frontier.put((1,child))
                #child.color=nodeColors["frontier"]
                reached.update({child.state:child})
            
        #node.color=nodeColors["expanded"]
      return None

    return program
  
 











def BestFirstSearchAgentProgramForShow(f=None):
  #with BFS we choose a node, n, with minimum value of some evaluation function, f (n).
    
    def program(problem):
      #print(111)
      steps = 0
      allNodeColors = []
      nodeColors = {k : 'white' for k in problem.graph.nodes()}

      node = Node(problem.initial)
      nodeColors[node.state] = "yellow"
      steps += 1
      allNodeColors.append(dict(nodeColors))

      #print(node.state)
      frontier = PriorityQueue()
      frontier.put((1,node))

      nodeColors[node.state] = "orange"
      steps += 1
      allNodeColors.append(dict(nodeColors))



      reached = {problem.initial:node}

      while frontier:
        node = frontier.get()[1]
        nodeColors[node.state] = "red"
        steps += 1
        allNodeColors.append(dict(nodeColors))
        #print(node)

        if problem.goal_test(node.state):
          nodeColors[node.state] = "green"
          steps += 1
          allNodeColors.append(dict(nodeColors))
          return (node,steps,allNodeColors)
          

        #reached.add(node.state)
        for child in node.expand(problem):
            if child.state not in reached or child.path_cost<reached[child.state].path_cost:
                frontier.put((1,child))
                nodeColors[child.state] = "orange"
                steps += 1
                allNodeColors.append(dict(nodeColors))

                reached.update({child.state:child})

        # modify the color of explored nodes to blue
        nodeColors[node.state] = "blue"
        steps += 1
        allNodeColors.append(dict(nodeColors))
            
      return None

    return program


# =====================================================================
# Task 2 - search programs for the Rescue Robot agents
# =====================================================================
import itertools                                      # itertools.count() = 0, 1, 2, ... forever


def BestFirstSearchWithF(f):                          # general Best-First Search; f = evaluation function
    def program(problem):                             # the actual search, run on one problem
        counter = itertools.count()                   # tie-breaker: when two nodes have equal f, older first
        node = Node(problem.initial)                  # root node = start cell, path cost 0
        frontier = PriorityQueue()                    # queue that always gives back the smallest item
        frontier.put((f(node), next(counter), node))  # add the root with priority f(root)
        reached = {problem.initial: node}             # best node found so far for each cell
        stats = {"expanded": 0, "generated": 1, "max_frontier": 1}   # counters for the comparison

        while not frontier.empty():                   # while there are nodes to look at
            _, _, node = frontier.get()               # take the node with the SMALLEST f
            if reached.get(node.state) is not node:   # a cheaper path to this cell was found later
                continue                              # -> this queue entry is outdated, skip it
            if problem.goal_test(node.state):         # is it the rescue target?
                program.stats = stats                 # save counters
                return node                           # done: return the goal node
            stats["expanded"] += 1                    # we expand this node
            for child in node.expand(problem):        # one child per legal action
                stats["generated"] += 1
                s = child.state                       # the child's cell
                if s not in reached or child.path_cost < reached[s].path_cost:
                    # new cell, or a cheaper way to a known cell
                    reached[s] = child                # remember it as the best
                    frontier.put((f(child), next(counter), child))   # add it to the queue
            stats["max_frontier"] = max(stats["max_frontier"], frontier.qsize())
        program.stats = stats                         # queue empty -> no solution
        return None

    program.stats = {}                                # counters live on the function itself
    return program                                    # give back the search function


def UniformCostSearchAgentProgram():                  # UCS
    return BestFirstSearchWithF(lambda node: node.path_cost)
    # Best-First Search with f(n) = g(n) = path cost -> always expands the cheapest path first


CUTOFF = "cutoff"                                     # result: "hit the depth limit somewhere"
FAILURE = None                                        # result: "no solution at all"


def is_cycle(node):                                   # does this node's cell already appear on its own path?
    state, p = node.state, node.parent                # start with the parent
    while p:                                          # walk up to the root
        if p.state == state:                          # same cell found among ancestors
            return True                               # -> going here would be a loop
        p = p.parent
    return False


def DepthLimitedSearch(problem, limit, stats=None):   # DLS: depth-first, but never deeper than `limit`
    stats = stats if stats is not None else {"expanded": 0, "generated": 0}

    def recursive_dls(node):                          # RECURSIVE-DLS from the lecture pseudocode
        cutoff_occurred = False                       # cutoff-occurred? <- false
        if problem.goal_test(node.state):             # GOAL-TEST
            return node                               # -> SOLUTION(node)
        elif node.depth == limit:                     # DEPTH[node] = limit
            return CUTOFF                             # -> cutoff
        stats["expanded"] += 1
        for successor in node.expand(problem):        # for each successor in EXPAND(node)
            stats["generated"] += 1
            if is_cycle(successor):                   # extra: skip loops (graph has cycles)
                continue
            result = recursive_dls(successor)         # result <- RECURSIVE-DLS(successor)
            if isinstance(result, str) and result == CUTOFF:
                cutoff_occurred = True                # if result = cutoff then cutoff-occurred? <- true
            elif result is not FAILURE:               # else if result != failure
                return result                         # -> a solution: pass it up
        return CUTOFF if cutoff_occurred else FAILURE # if cutoff-occurred? return cutoff else failure

    return recursive_dls(Node(problem.initial))       # always start from the initial state


def IDSearchAgentProgram(max_depth=None, verbose=True):   # Iterative Deepening (Iterative DLS)
    def program(problem):
        stats = {"expanded": 0, "generated": 0, "iterations": 0}
        for depth in itertools.count():               # depth limit = 0, 1, 2, 3, ...
            if max_depth is not None and depth > max_depth:
                break                                 # optional safety limit (not used by default)
            stats["iterations"] += 1
            result = DepthLimitedSearch(problem, depth, stats)   # new DLS from the SAME initial state
            if isinstance(result, str) and result == CUTOFF:     # limit too small
                if verbose:
                    print(f"   IDS depth limit {depth}: cutoff")
                continue                              # -> try a bigger limit
            if verbose:
                print(f"   IDS depth limit {depth}: " +
                      ("solution found" if result is not None else "failure - no solution exists"))
            program.stats = stats
            return result                             # goal node, or None if no solution exists
        program.stats = stats
        return None

    program.stats = {}
    return program
