"""
cspVisualization.py   [Lab7 added]
------------------------------------
PyVis drawing helpers for Lab 7 (Task 1.3 - constraint graph of the
Dinner Accommodation Problem).

The produced .html files use lib/bindings/utils.js (shipped with the lab),
so open them from the project's main folder.
"""

from pyvis.network import Network


def visualize_dinner_csp(csp, filename="task1_dinner_constraints.html",
                         assignment=None, domains=None):
    """Draw the constraint graph of a DinnerCSP with PyVis.

    Nodes  : the 5 colleagues (variables). Hover shows the domain.
             If `assignment` is given, the chair number is shown in the label.
    Edges  : one edge per pair of neighbours.
             grey  -> only the AllDifferent constraint (different chairs)
             red   -> AllDifferent + "must NOT sit next to each other"
                      (the edge label explains why)
    domains: optional dict to show instead of csp.domains (e.g. after AC-3)
    """
    net = Network(height="550px", width="100%", directed=False,
                  notebook=False, cdn_resources="local",
                  heading="Task 1 - Dinner Accommodation constraint graph")

    # Persons involved in a "not adjacent" conflict get a different colour
    in_conflict = {p for pair in csp.conflicts for p in pair}

    # ---- nodes -------------------------------------------------------------
    for person in csp.variables:
        dom = (domains or csp.domains)[person]
        label = person if not assignment else f"{person}\nchair {assignment[person]}"
        net.add_node(person, label=label, shape="circle",
                     color="#f8b4b4" if person in in_conflict else "#bfe3c0",
                     font={"size": 22},
                     title=f"{person}: domain = {list(dom)}")

    # ---- edges (each undirected pair only once) -----------------------------
    added = set()
    for X in csp.variables:
        for Y in csp.neighbors[X]:
            pair = frozenset((X, Y))
            if pair in added:
                continue
            added.add(pair)
            if pair in csp.conflicts:
                net.add_edge(X, Y, color="red", width=4,
                             label=csp.conflicts[pair],
                             title="different chairs AND not adjacent")
            else:
                net.add_edge(X, Y, color="#bbbbbb", width=1,
                             title="different chairs (AllDifferent)")

    net.toggle_physics(True)
    net.write_html(filename)
    return filename
