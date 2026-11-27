"""
dinner_app.py   [Lab7 added]  -  Task 1.6
==========================================
Streamlit web-service that visualises, step by step, how backtracking search
assigns chairs to the 5 colleagues of the Dinner Accommodation Problem.

Run from the project's main folder:
    streamlit run dinner_app.py

What the page shows
  * sidebar   : pick the variable heuristic (first / MRV / MRV+Degree),
                the value heuristic (unordered / LCV) and the variable order
  * metrics   : assignments, search nodes and backtracks of that run
  * the table : drawn as SVG, updated for the selected step
                green  = person seated, red = value rejected (conflict),
                orange = assignment undone (backtrack)
  * a slider + "Play" button to move through the search
  * the step log and a comparison of all heuristics
"""

import time

import pandas as pd
import streamlit as st

from src.CSPS import DinnerCSP, DINNER_CONFLICTS, chairs_adjacent
from src.algorithms import (backtracking_search, replay_trace,
                            first_unassigned_variable, mrv, mrv_degree,
                            unordered_domain_values, lcv)

# -----------------------------------------------------------------------------
# Heuristic choices shown in the sidebar (label -> function)
# -----------------------------------------------------------------------------
VAR_HEURISTICS = {
    "First unassigned (basic)": first_unassigned_variable,
    "MRV": mrv,
    "MRV + Degree": mrv_degree,
}
VAL_HEURISTICS = {
    "Unordered (basic)": unordered_domain_values,
    "LCV": lcv,
}

# (x, y) position of every chair in the SVG, same layout as the task picture
CHAIR_XY = {1: (200, 40), 2: (340, 120), 3: (340, 220),
            4: (200, 300), 5: (60, 220), 6: (60, 120)}


def run_search(order, var_h, val_h):
    """Build a fresh DinnerCSP (so counters start at 0), run backtracking with
    the chosen heuristics and return (solution, trace, csp)."""
    csp = DinnerCSP(people=list(order))
    trace = []
    solution = backtracking_search(csp, VAR_HEURISTICS[var_h],
                                   VAL_HEURISTICS[val_h], trace=trace)
    return solution, trace, csp


def table_svg(assignment, highlight=None):
    """Return an SVG drawing of the table.
    assignment : {person: chair} currently seated
    highlight  : (action, person, chair) of the current step, or None"""
    seat = {chair: person for person, chair in assignment.items()}
    parts = ['<svg width="400" height="340" xmlns="http://www.w3.org/2000/svg">',
             # the table itself
             '<rect x="110" y="80" width="180" height="180" rx="8" '
             'fill="#d9c3a5" stroke="#7a5c3a" stroke-width="3"/>',
             '<text x="200" y="175" text-anchor="middle" font-size="18" '
             'fill="#5a4026">TABLE</text>']

    # red dashed lines between seated people who are enemies AND adjacent
    # (never happens in an accepted state, kept as a visual sanity check)
    for pair in DINNER_CONFLICTS:
        p, q = tuple(pair)
        if p in assignment and q in assignment and chairs_adjacent(assignment[p], assignment[q]):
            (x1, y1), (x2, y2) = CHAIR_XY[assignment[p]], CHAIR_XY[assignment[q]]
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                         'stroke="red" stroke-dasharray="4"/>')

    # every chair: colour depends on who sits there / what the step did
    for chair, (x, y) in CHAIR_XY.items():
        person, fill = seat.get(chair, ""), "#ffffff"
        if person:
            fill = "#a5d6a7"                                   # seated -> green
        if highlight and highlight[2] == chair:
            action, who, _ = highlight
            if action == "conflict":
                person, fill = who, "#ef9a9a"                  # rejected -> red
            elif action == "backtrack":
                person, fill = who, "#ffcc80"                  # undone -> orange
            elif action == "assign":
                fill = "#66bb6a"                               # just seated -> dark green
        parts.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{fill}" '
                     'stroke="#333" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y + 7}" text-anchor="middle" '
                     f'font-size="22" font-weight="bold">{person}</text>')
        parts.append(f'<text x="{x}" y="{y - 34}" text-anchor="middle" '
                     f'font-size="11" fill="#555">chair {chair}</text>')
    parts.append('</svg>')
    return "".join(parts)


def describe(step):
    """Human-readable sentence for one trace step."""
    action, var, value = step
    return {
        "assign": f"Seat {var} on chair {value}",
        "conflict": f"{var} on chair {value} violates a constraint -> rejected",
        "backtrack": f"Dead end below -> remove {var} from chair {value}",
        "solution": "All 5 colleagues are seated - solution found!",
        "failure": "No solution exists",
    }[action]


# =============================================================================
# Page layout
# =============================================================================
st.set_page_config(page_title="Dinner Accommodation - Backtracking", layout="wide")
st.title("Task 1 - Dinner Accommodation Problem")
st.caption("A despises B · B argues with E · C is B's manager "
           "→ those pairs must not sit next to each other. 5 people, 6 chairs.")

# ---- sidebar: choose the search configuration --------------------------------
st.sidebar.header("Search settings")
var_h = st.sidebar.selectbox("Variable ordering", list(VAR_HEURISTICS))
val_h = st.sidebar.selectbox("Value ordering", list(VAL_HEURISTICS))
order = st.sidebar.text_input("Variable order (csp.variables)", "ABCDE").upper()
speed = st.sidebar.slider("Play speed (seconds per step)", 0.1, 2.0, 0.6)

# validate the order: it must be a permutation of A..E
if sorted(order) != list("ABCDE"):
    st.sidebar.error("Variable order must contain A, B, C, D, E exactly once")
    st.stop()

# ---- run the search -------------------------------------------------------------
solution, trace, csp = run_search(order, var_h, val_h)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Variable assignments", csp.nassigns)
c2.metric("Search nodes explored", csp.nodes_explored)
c3.metric("Backtracks", csp.nbacktracks)
c4.metric("Trace steps", len(trace))

# ---- step selection ---------------------------------------------------------------
# When settings change, the old step number may be out of range -> reset it
config = (var_h, val_h, order)
if st.session_state.get("config") != config:
    st.session_state.config = config
    st.session_state.step = 0

# [fix] Streamlit does not allow changing a widget's value after the widget
# is drawn. So "Play" only stores the target step in "jump_to"; here, BEFORE
# the slider is created, we move the slider to that step.
if "jump_to" in st.session_state:
    st.session_state.step = st.session_state.pop("jump_to")

left, right = st.columns([1, 1])
with left:
    st.slider("Step", 0, len(trace), key="step")
    play = st.button("▶ Play from current step")
    board = st.empty()          # placeholder that we redraw while playing
    caption = st.empty()


def draw(k):
    """Draw the table after the first k steps of the trace."""
    assignment = replay_trace(trace, k)
    step = trace[k - 1] if k > 0 else None
    highlight = step if step and step[0] in ("assign", "conflict", "backtrack") else None
    board.markdown(table_svg(assignment, highlight), unsafe_allow_html=True)
    caption.info(f"Step {k}/{len(trace)}: " + (describe(step) if step else "Empty table - search starts"))


if play:
    # animate from the current step to the end, then remember where we stopped
    for k in range(st.session_state.step, len(trace) + 1):
        draw(k)
        time.sleep(speed)
    st.session_state.jump_to = len(trace)   # applied before the slider on the rerun
    st.rerun()
else:
    draw(st.session_state.step)

# ---- right column: step log ------------------------------------------------------
with right:
    st.subheader("Search log")
    log = pd.DataFrame([{"step": i + 1, "action": a, "person": v, "chair": c,
                         "what happens": describe((a, v, c))}
                        for i, (a, v, c) in enumerate(trace)])
    st.dataframe(log, hide_index=True, height=420)
    if solution:
        st.success("Final seating: " + ", ".join(f"{p}→{solution[p]}" for p in sorted(solution)))

# ---- comparison of every heuristic on the same CSP ------------------------------------
st.subheader("Comparison of heuristics (same variable order)")
rows = []
for vh in VAR_HEURISTICS:
    for lh in VAL_HEURISTICS:
        _, _, c = run_search(order, vh, lh)
        rows.append({"variable ordering": vh, "value ordering": lh,
                     "assignments": c.nassigns, "nodes": c.nodes_explored,
                     "backtracks": c.nbacktracks})
st.dataframe(pd.DataFrame(rows), hide_index=True)
st.caption("Tip: try the variable order EDCAB or ADECB (B placed last) - the basic search "
           "backtracks 10 times, while MRV, MRV + Degree and LCV need no backtracking.")
