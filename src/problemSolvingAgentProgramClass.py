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
        """Formulate a goal and problem, then
        search for a sequence of actions to solve it."""
        #4-phase problem-solving process
        #print(0)
        temp=self.state
        self.state = self.update_state(self.state, percept)
        
        if not self.seq:
            goal = self.formulate_goal(self.state)
            
            if isinstance(goal, list) and len(goal)>1:
                  percept=self.state                         
                  while len(self.goal)>0:
                        #4-phase problem-solving process
                        self.state = self.update_state(self.state, percept)
                        current_goal=self.goal[0]
                        goal = current_goal
                        problem = self.formulate_problem(self.state, goal)
                        self.seq.extend (self.search(problem))
                        percept=current_goal
                        self.goal.remove(goal)
                  self.state = temp
            else:
                  print(f"Hi, I have the only goal: {goal}")
                  problem = self.formulate_problem(self.state, goal)
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