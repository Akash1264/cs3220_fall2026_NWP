"""
sudoku_app.py   [Lab7 added]  -  Task 2.2
==========================================
Streamlit web-service that visualises backtracking search solving the
Asterisk Sudoku from Assignment 6.

Run from the project's main folder:
    streamlit run sudoku_app.py

What the page shows
  * sidebar : search strategy
                - Basic backtracking (first unassigned variable)
                - AC-3 first, then basic backtracking
                - MRV
                - MRV + Degree
  * metrics : assignments, search nodes, backtracks, time
  * the grid: given digits in black, digits placed by the search in blue,
              the cell changed in the current step in yellow (assign) or
              red (backtrack), asterisk cells shaded pink
  * a slider (with a jump size, because basic search has 600k+ steps)
    and a "Play" button
"""

import time

import streamlit as st

from src.CSPS import (AsteriskSudokuCSP, ASTERISK_PUZZLE, ASTERISK_CELLS,
                      sudoku_cell, check_sudoku_solution)
from src.algorithms import (AC3, backtracking_search, replay_trace,
                            first_unassigned_variable, mrv, mrv_degree)

STRATEGIES = ["MRV", "MRV + Degree", "AC-3 + basic backtracking",
              "Basic backtracking"]

# Cells printed in the puzzle (they never change during the search)
GIVENS = {sudoku_cell(r, c): ASTERISK_PUZZLE[r][c]
          for r in range(9) for c in range(9) if ASTERISK_PUZZLE[r][c]}


@st.cache_data(show_spinner="Running backtracking search ...")
def run_search(strategy):
    """Solve the puzzle with the chosen strategy and return the statistics and
    the trace. Cached, so the (slow) basic search runs only once per session.

    Conflicts are not recorded (trace_conflicts=False) - the basic search
    rejects over a million values, recording them would waste memory."""
    csp = AsteriskSudokuCSP()
    start = time.time()
    if strategy == "AC-3 + basic backtracking":
        AC3(csp, verbose=False)        # prune domains first, then search
    select = {"MRV": mrv, "MRV + Degree": mrv_degree}.get(strategy,
                                                           first_unassigned_variable)
    trace = []
    solution = backtracking_search(csp, select, trace=trace, trace_conflicts=False)
    return {"solution": solution, "trace": trace,
            "assigns": csp.nassigns, "nodes": csp.nodes_explored,
            "backtracks": csp.nbacktracks, "seconds": time.time() - start}


def grid_html(values, changed=None, action=None):
    """HTML table of the 9x9 grid.
    values  : {cell: digit} of the current partial assignment
    changed : cell modified in the current step (highlighted)
    action  : 'assign' (yellow) or 'backtrack' (red)"""
    html = ['<table style="border-collapse:collapse;font-size:22px;'
            'font-family:monospace;margin:auto">']
    for r in range(9):
        html.append("<tr>")
        for c in range(9):
            cell = sudoku_cell(r, c)
            # thick borders around the 3x3 boxes
            top = "3px" if r % 3 == 0 else "1px"
            left = "3px" if c % 3 == 0 else "1px"
            bottom = "3px" if r == 8 else "1px"
            right = "3px" if c == 8 else "1px"
            bg = "#f8d7e3" if cell in ASTERISK_CELLS else "#ffffff"   # asterisk shading
            colour, weight, digit = "#1565c0", "normal", values.get(cell, "")
            if cell in GIVENS:                                         # given digit
                colour, weight, digit = "#000000", "bold", GIVENS[cell]
            if cell == changed:                                        # current step
                bg = "#fff176" if action == "assign" else "#ef9a9a"
            html.append(f'<td title="{cell}" style="width:40px;height:40px;'
                        f'text-align:center;background:{bg};color:{colour};'
                        f'font-weight:{weight};border:1px solid #444;'
                        f'border-top-width:{top};border-left-width:{left};'
                        f'border-bottom-width:{bottom};border-right-width:{right}">'
                        f'{digit}</td>')
        html.append("</tr>")
    html.append("</table>")
    return "".join(html)


# =============================================================================
# Page layout
# =============================================================================
st.set_page_config(page_title="Asterisk Sudoku - Backtracking", layout="wide")
st.title("Task 2 - Asterisk Sudoku solved with backtracking search")
st.caption("Pink cells = the asterisk, which must also contain 1-9. "
           "Black = given, blue = placed by the search.")

strategy = st.sidebar.selectbox("Search strategy", STRATEGIES)
jump = st.sidebar.select_slider("Steps per Play frame",
                                [1, 5, 25, 100, 1000, 10000], value=1)
speed = st.sidebar.slider("Seconds per frame", 0.02, 1.0, 0.15)

result = run_search(strategy)
trace = result["trace"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Variable assignments", f'{result["assigns"]:,}')
c2.metric("Search nodes explored", f'{result["nodes"]:,}')
c3.metric("Backtracks", f'{result["backtracks"]:,}')
c4.metric("Time (s)", f'{result["seconds"]:.2f}')

# reset the step when the strategy changes (old step may be out of range)
if st.session_state.get("strategy") != strategy:
    st.session_state.strategy = strategy
    st.session_state.step = 0

# [fix] Streamlit does not allow changing a widget's value after the widget
# is drawn. So "Play" only stores the target step in "jump_to"; here, BEFORE
# the slider is created, we move the slider to that step.
if "jump_to" in st.session_state:
    st.session_state.step = st.session_state.pop("jump_to")

st.slider("Step", 0, len(trace), key="step")
play = st.button("▶ Play from current step")
board = st.empty()
caption = st.empty()


def draw(k):
    """Draw the grid after the first k trace steps."""
    values = replay_trace(trace, k)
    action, var, value = trace[k - 1] if k > 0 else (None, None, None)
    board.markdown(grid_html(values, var, action), unsafe_allow_html=True)
    text = {"assign": f"put {value} in {var}",
            "backtrack": f"dead end -> remove {value} from {var}",
            "solution": "solution found!"}.get(action, "start: only the givens")
    caption.info(f"Step {k:,}/{len(trace):,}: {text}   ·   "
                 f"{sum(c not in GIVENS for c in values)} of {81 - len(GIVENS)} "
                 f"empty cells filled")


if play:
    k = st.session_state.step
    while k < len(trace):
        k = min(k + jump, len(trace))
        draw(k)
        time.sleep(speed)
    st.session_state.jump_to = len(trace)   # applied before the slider on the rerun
    st.rerun()
else:
    draw(st.session_state.step)

# final check of the solution (all rows, columns, boxes and the asterisk)
if result["solution"]:
    ok = check_sudoku_solution(result["solution"])
    st.success("Solved - every row, column, box and the asterisk contains 1-9."
               if ok else "Search returned an invalid grid!")
