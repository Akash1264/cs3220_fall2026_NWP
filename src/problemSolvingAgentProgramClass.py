class SimpleProblemSolvingAgentProgram:
  #Abstract framework for a problem-solving agent
  def __init__(self, initial_state=None):
        """State is an abstract representation of the state
        of the world, and seq is the list of actions required
        to get to a particular state from the initial state(root)."""
        self.state = initial_state
        self.seq = []#solution.
        
        self.performance=0
        self.alive=True

  def __call__(self, percept, curGoal=None):
        """Problem-Solving Agent:
    Formulate a goal and problem, then search for
    a sequence of actions that solves the problem.
    
    The process has 4 main phases:
        1. Goal Formulation
        2. Problem Formulation
        3. Search
        4. Execution of the resulting action sequence"""


      # Update the agent's current state using the new percept.
      # This provides the current state from which the problem
      # solving process will begin.
      
        
        temp=self.state
        self.state = self.update_state(self.state, percept)

      # If there is no existing sequence of actions to execute,
      # start a new problem-solving process.
        if not self.seq:

      # =====================================================
        # PHASE 1: GOAL FORMULATION
        # =====================================================
        # Determine what the agent wants to achieve based
        # on the current state.     
      # =====================================================
            goal = self.formulate_goal(self.state)
            
            if isinstance(goal, list) and len(goal)>1: # If multiple goals have been formulated, solve them one at a time.
                  percept=self.state                         
                  while len(self.goal)>0:
                        # Update the current state before solving the next goal.
                        self.state = self.update_state(self.state, percept)
                        current_goal=self.goal[0]
                        goal = current_goal

                        # =================================================
                        # PHASE 2: PROBLEM FORMULATION
                        # =================================================
                        # Convert the current goal into a formal
                        # search problem.
                        #
                        # The problem specifies:
                        #   - Initial state
                        #   - Actions
                        #   - Transition model
                        #   - Goal test
                        #   - Path cost
                        # =================================================
                        problem = self.formulate_problem(self.state, goal)


                        # =================================================
                        # PHASE 3: SEARCH
                        # =================================================
                        # Search the state space to find a sequence
                        # of actions that transforms the current state
                        # into a goal state.
                        #
                        # Example:
                        # A → C → F → G
                        #
                        # search(problem) returns the solution path,
                        # represented as a sequence of actions.
                        # =================================================
                        self.seq.extend (self.search(problem))


                        # The achieved goal becomes the basis for continuing with the next goal.
                        percept=current_goal

                        # Remove the completed goal.

                        self.goal.remove(goal)
                  self.state = temp
            else: # the single goal case
                  # PHASE 2: PROBLEM FORMULATION
                  problem = self.formulate_problem(self.state, goal)
                  
                  # PHASE 3: SEARCH
                  self.seq = self.search(problem)                 
                  
                  
                        
            if not self.seq:
                return None
        else:
              print("I have already don my work. Find someone else")
              
        #return self.seq.pop(0)
        return None

  def update_state(self, state, percept):
        raise NotImplementedError

  def formulate_goal(self, state):
        raise NotImplementedError

  def formulate_problem(self, state, goal):
        raise NotImplementedError

  def search(self, problem):
        raise NotImplementedError