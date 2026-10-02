#This base class represents ANY physical object that can appear in an Environment.
class Thing:

  def __repr__(self):
    """Return a string representation of this Thing (as script name or class name)"""
    return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

  def is_alive(self):
    """Things that are 'alive' should return true."""
    return hasattr(self, 'alive') and self.alive

  def show_state(self):
    """Display the agent's internal state. Subclasses should override."""
    print("I don't know how to show_state.")