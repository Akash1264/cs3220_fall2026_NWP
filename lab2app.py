# Lab 2 - Simple Intelligent Agents: web app with 3 tabs (one per task)
# Run:  streamlit run lab2app.py
import io
import contextlib
from pathlib import Path

import streamlit as st

from src.locations import loc_A, loc_B, loc_C, loc_D
from src.agentClass import CatAgent, proCatAgent, MouseAgent

# Task 1
from src.CompanyEnvironmentClass import CompanyEnvironment
from src.Task1_YourRecipientsClasses import OfficeManager, Student, ITStaff
from src.agents import ReflexAgentA2pro

# Task 2
from src.catFriendlyHouse_envClass import catFriendlyHouse_env, catFriendlyHouse2_env
from src.catFriendlyHouse_membersClass import Milk, Sausage, Mouse, Dog
from src.agents import ReflexAgentA3pro

# Task 3
from src.agents import RandomMouseAgent, ReflexAgentA4pro

st.set_page_config(page_title="Lab 2 - Simple Agents", page_icon="🤖", layout="wide")

ROOM_NAMES = {loc_A: "A", loc_B: "B", loc_C: "C", loc_D: "D"}
MAX_STEPS = 40
IMG_DIR = Path(__file__).parent / "imgs"


# ---------------------------------------------------------------- helpers
def captured(fn, *args):
    """Run fn and return (result, everything it printed)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(*args)
    return result, buf.getvalue()


def icon(obj):
    if isinstance(obj, OfficeManager):
        return "🧑‍💼"
    if isinstance(obj, ITStaff):
        return "👨‍💻"
    if isinstance(obj, Student):
        return "🧑‍🎓"
    if isinstance(obj, Milk):
        return "🥛"
    if isinstance(obj, Sausage):
        return "🌭"
    if isinstance(obj, Mouse):
        return "🐭"
    if isinstance(obj, Dog):
        return "🐶"
    if isinstance(obj, MouseAgent):
        if getattr(obj, "eaten", False):
            return "🍽️🐭"
        return "🐭" if obj.alive else "😵🐭"
    if isinstance(obj, (CatAgent, proCatAgent)):
        arrow = "➡️" if obj.direction else "⬅️"
        return f"🐱{arrow}"
    return "🚚"  # delivery agent


def draw_rooms(env):
    cols = st.columns(len(env.locations))
    for col, loc in zip(cols, env.locations):
        agents_here = [a for a in env.agents
                       if a.location == loc and not getattr(a, "eaten", False)]
        things_here = env.list_things_at(loc)
        content = " ".join(icon(x) for x in agents_here + things_here) or "·"
        with col.container(border=True):
            st.markdown(f"**Room {ROOM_NAMES[loc]}** `{loc}`")
            st.markdown(
                f"<div style='font-size:2.6rem;text-align:center;min-height:4rem'>{content}</div>",
                unsafe_allow_html=True,
            )


def controls(key, new_fn):
    """Buttons + state handling shared by all tabs."""
    if key not in st.session_state:
        st.session_state[key] = captured(new_fn)[0] | {"log": "", "steps": 0, "last": []}
    s = st.session_state[key]
    env = s["env"]

    c1, c2, c3 = st.columns(3)
    if c1.button("🔄 New random layout", key=f"{key}_new", use_container_width=True):
        s, out = captured(new_fn)
        st.session_state[key] = s | {"log": out, "steps": 0, "last": []}
        st.rerun()
    if c2.button("▶️ Run one step", key=f"{key}_step", use_container_width=True,
                 disabled=env.is_done()):
        s["last"], out = captured(env.step)
        s["steps"] += 1
        s["log"] += f"\n----- step {s['steps']} -----\n" + out
        st.rerun()
    if c3.button("⏩ Run to the end", key=f"{key}_run", use_container_width=True,
                 disabled=env.is_done()):
        while not env.is_done() and s["steps"] < MAX_STEPS:
            s["last"], out = captured(env.step)
            s["steps"] += 1
            s["log"] += f"\n----- step {s['steps']} -----\n" + out
        st.rerun()
    return s


def show_status(s):
    env = s["env"]
    m = st.columns(len(env.agents) + 2)
    m[0].metric("Steps", s["steps"])
    for col, a in zip(m[1:], env.agents):
        col.metric(f"{icon(a)} {type(a).__name__} performance", a.performance)
    if s["last"]:
        m[-1].metric("Last actions", ", ".join(str(x) for x in s["last"] if x != "") or "-")
    if env.is_done():
        st.success("Simulation finished. Click **New random layout** to try again.")
    with st.expander("Agent log (printed output)"):
        st.code(s["log"] or "No steps yet.", language=None)


# ---------------------------------------------------------------- task setups
def new_task1():
    env = CompanyEnvironment()
    for r in (ITStaff(), Student(), OfficeManager()):
        env.add_thing(r)
    agent = ReflexAgentA2pro()
    env.add_thing(agent)
    return {"env": env, "agent": agent}


def new_task2():
    env = catFriendlyHouse_env()
    env.add_thing(Milk(weight=200, calories=50))
    env.add_thing(Sausage(weight=150, calories=505))
    env.add_thing(Mouse(size=2))
    cat = ReflexAgentA3pro()
    env.add_thing(cat)
    return {"env": env, "agent": cat}


def new_task3():
    env = catFriendlyHouse2_env()
    env.add_thing(RandomMouseAgent())
    if st.session_state.get("t3_dog", False):
        env.add_thing(Dog())
    cat = ReflexAgentA4pro()
    env.add_thing(cat)
    return {"env": env, "agent": cat}


# ---------------------------------------------------------------- UI
st.title("🤖 Lab 2 - Simple Intelligent Agents")
tab1, tab2, tab3 = st.tabs(["📦 Task 1: Delivery Agent",
                            "🐱 Task 2: Cat-Agent",
                            "🐱 vs 🐭 Task 3: Cat vs Mouse"])

with tab1:
    st.subheader("Reflex Delivery Agent - office with 4 rooms")
    st.caption("🚚 agent gives 📬 mail to 🧑‍💼 Office Manager, 🍩 donuts to 👨‍💻 IT, 🍕 pizza to 🧑‍🎓 Student. "
               "Moves Left → Right and stops after the last room. Delivery +3, move -1.")
    s = controls("t1", new_task1)
    draw_rooms(s["env"])
    show_status(s)

with tab2:
    left, right = st.columns([4, 1])
    with left:
        st.subheader("Reflex Cat-Agent - Cat-Friendly-House with 3 rooms")
        st.caption("🐱 Drinks 🥛, eats 🌭, catches 🐭 (only if strong enough), each move -1. "
                   "Turns around at the last room if food is left; room A is the end of the hunt.")
    if (IMG_DIR / "cat_milk.png").exists():
        right.image(str(IMG_DIR / "cat_milk.png"), width=120)
    s = controls("t2", new_task2)
    draw_rooms(s["env"])
    show_status(s)

with tab3:
    st.subheader("Multi-agent: Reflex Cat vs Random Mouse - 4 rooms")
    st.caption("🐭 moves randomly (-1 per move, 😵 = exhausted but still catchable). "
               "🐱 moves -5, catch +10 if cat performance ≥ mouse performance × 5, otherwise -10. "
               "🐶 fight: win +20 if performance ≥ 10, else -10. Cat performance ≤ 0 → GAME OVER.")
    st.checkbox("Add a 🐶 Dog (applies on New random layout)", key="t3_dog")
    s = controls("t3", new_task3)
    draw_rooms(s["env"])
    show_status(s)
