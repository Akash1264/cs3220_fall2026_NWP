# Import dependencies
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw

from src.trivialVacuumEnvironmentClass import TrivialVacuumEnvironment
from src.agents import RandomVacuumAgent

IMG_DIR = Path(__file__).parent / "imgs"


def drawImg(a, b, agentAt):
    """Draw the environment in memory: green = clean, brown = dirty, blue dot = agent."""
    img = Image.new("RGB", (400, 200), "white")
    d = ImageDraw.Draw(img)
    for i, (state, label) in enumerate([(a, "A"), (b, "B")]):
        x = i * 200
        d.rectangle([x, 0, x + 199, 199],
                    fill="#c8e6c9" if state == "clean" else "#a1887f", outline="black")
        d.text((x + 10, 10), f"{label}: {state}", fill="black")
        if agentAt == label:
            d.ellipse([x + 70, 70, x + 130, 130], fill="#1976d2")
            d.text((x + 80, 140), "Agent", fill="black")
    return img


def getImg(agentLoc, envState):
    """Works whether loc_B is (1, 0) or (0, 1). Uses imgs/ files if present,
    otherwise draws the picture itself."""
    loc_A, loc_B = sorted(envState.keys())  # (0,0) always sorts first
    a = envState[loc_A].lower()
    b = envState[loc_B].lower()

    if agentLoc == loc_A:
        agentAt, filename = "A", f"a_{a}_Agent__b_{b}.jpg"
    elif agentLoc == loc_B:
        agentAt, filename = "B", f"a_{a}__b_{b}_Agent.jpg"
    else:
        raise ValueError(f"Unknown agent location {agentLoc}; env locations are {loc_A}, {loc_B}")

    path = IMG_DIR / filename
    if path.exists():
        return Image.open(path)
    return drawImg(a, b, agentAt)


def drawBtn(e, a):
    st.button("Run One Agent's Step", on_click=AgentStep, args=[[e, a]])


def AgentStep(opt):
    st.session_state["clicked"] = True
    e, a = opt[0], opt[1]

    if e.is_agent_alive(a):
        stepActs = e.step()
        st.success("Agent decided to do: {}.".format(",".join(stepActs)))
        st.success("RandomVacuumAgent is located at {} now.".format(a.location))
        st.info("Current Agent performance: {}.".format(a.performance))
        st.info("State of the Environment: {}.".format(e.status))
    else:
        st.error("Agent in location {} and it is dead.".format(a.location))

    st.image(getImg(a.location, e.status), caption="Agent is here")


def main():
    if "clicked" not in st.session_state:
        st.session_state["clicked"] = False

    if not st.session_state["clicked"]:
        st.title('Simple Agents - lab2. Example1')
        st.header("_Initial Env._", divider=True)

        a1 = RandomVacuumAgent()
        st.info(f"{a1} has the initial performance: {a1.performance}")

        e1 = TrivialVacuumEnvironment()
        st.info("State of the Environment: {}.".format(e1.status))

        e1.add_thing(a1)

        st.info("Agent in location {}.".format(a1.location))
        st.image(getImg(a1.location, e1.status), caption="Agent is here")

        drawBtn(e1, a1)

    if st.session_state["clicked"]:
        st.warning("Agent Step Done!")


if __name__ == '__main__':
    main()
