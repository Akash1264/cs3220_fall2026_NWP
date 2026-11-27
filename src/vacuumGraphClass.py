from src.graphClass import Graph

class vacuumGraph(Graph):
  def __init__(self, graph_dict=None,locations=None):
    #self.g=dict()
    self.origin=graph_dict
    self.graph_dict = dict()
    #super().__init__(graph_dict)
    self.make_graph(graph_dict)
    self.locations=locations


  def make_graph(self,graph_dict):
    for a in graph_dict.keys():
      #print(self.graph_dict[a].items())
      for (act, b) in graph_dict[a].items():
        self.connect(a, b, 1)

  def connect(self, A, B, distance):
    #print(self.g)
    self.graph_dict.setdefault(A, {})[B] = distance

  def nodes(self):
    s1 = set([k for k in self.graph_dict.keys()])
    #s2 = set([v2 for v in self.graph_dict.values() for k2, v2 in v.items()])
    #nodes = s1.union(s2)
    nodes=s1
    return list(nodes)

  def get(self, a, b=None):
        """Return a link distance or a dict of {node: distance} entries.
        .get(a,b) returns the distance or None;
        .get(a) returns a dict of {node: distance} entries, possibly {}."""
        links = self.graph_dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)
  
  def getLocation(self,a):
      return self.locations.get(a)  
