class Node:
    """A node in a search tree. 
    Contains a pointer to the parent (the node that this is a successor of) 
    and to the actual state for this node. 
    !!! Note that if a state is arrived at by two paths, then there are two nodes with
    the same state. 
    Also includes the action that got us to this state, 
    and  the total path_cost (also known as g) to reach the node. 
    You will not need to     subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1
        self.color="white" # for search vis-n

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state
    '''
    We can expand the node, by considering
    the available ACTIONS for that state
    '''
    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        #using the RESULT function to see where those actions lead to
        next_state = problem.result(self.state, action)
        # and generating a new node (called a child node)
        #for each of the resulting states
        next_node = Node(next_state, self, action, problem.path_cost(self.path_cost, self.state, action, next_state))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        '''
        Following the PARENT pointers back from a node allows us to 
        recover the states and actions along the path to that node. 
        Doing this from a goal node gives us the solution
        '''
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state
