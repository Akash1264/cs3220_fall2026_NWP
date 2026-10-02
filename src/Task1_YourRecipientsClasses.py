from src.thingClass import Thing

class OfficeManager(Thing):
  def __init__(self, name='Office Manager'):
    self.name = name
    self.order = 'daily mail'

class ITStaff(Thing):
  def __init__(self, name='IT Specialist'):
    self.name = name
    self.order = 'donuts from Tim Hortons'

class Student(Thing):
  def __init__(self, name='Student'):
    self.name = name
    self.order = 'pizza from Domino Pizza'
