"""Run with: python -m streamlit run streamlit_app.py"""
import random
import time
import streamlit as st
from algorithm import parse_array, simulate

st.set_page_config(page_title="Andrew's Merge Sort Lab", page_icon=":material/sort:", layout="wide")
st.session_state.setdefault("events", simulate([38, 27, 43, 3, 9, 82, 10]))
st.session_state.setdefault("position", 0)
st.session_state.setdefault("playing", False)
st.session_state.setdefault("last_tick", time.monotonic())
st.session_state.setdefault("array_input", "38, 27, 43, 3, 9, 82, 10")
st.session_state.setdefault("seek", 1)


def load(values):
    st.session_state.events = simulate(values)
    st.session_state.position = 0
    st.session_state.seek = 1
    st.session_state.playing = False


def randomize():
    values = [random.randrange(100) for _ in range(8)]
    st.session_state.array_input = ", ".join(map(str, values))
    load(values)


def navigate(offset=None):
    st.session_state.playing = False
    st.session_state.position = 0 if offset is None else max(0, min(len(st.session_state.events)-1, st.session_state.position + offset))
    st.session_state.seek = st.session_state.position + 1


def seek():
    st.session_state.playing = False
    st.session_state.position = st.session_state.seek - 1


def toggle():
    st.session_state.playing = not st.session_state.playing
    st.session_state.last_tick = time.monotonic()


def display_items(items, pointer=None):
    if not items:
        st.caption("Empty buffer")
        return
    text = []
    for index, (value, origin) in enumerate(items):
        label = f"{value} (#{origin})"
        text.append(f":orange-background[**{label}**]" if index == pointer else f"`{label}`")
    st.markdown(" · ".join(text))


st.caption("DESIGN AND ANALYSIS OF ALGORITHMS · INTERACTIVE SIMULATOR")
st.title("Andrew's Merge Sort Lab")
st.write("Explore divide and conquer: split, compare, and merge an array one step at a time.")
with st.form("input_form"):
    st.text_input("Array elements", key="array_input", help="1–16 integers from −999 to 999; commas or spaces separate values.")
    submitted = st.form_submit_button("Load array", type="primary")
if submitted:
    try:
        load(parse_array(st.session_state.array_input))
    except ValueError as error:
        st.error(str(error))
st.button("Random array", on_click=randomize)
speed = st.selectbox("Step duration", [0.35, 0.9, 1.6], index=1, format_func=lambda s:f"{s} seconds")


@st.fragment(run_every=0.2)
def simulator():
    state = st.session_state
    if state.playing and time.monotonic() - state.last_tick >= speed:
        state.position = min(state.position + 1, len(state.events)-1)
        state.seek = state.position + 1
        state.last_tick = time.monotonic()
        if state.position == len(state.events)-1:
            state.playing = False
    with st.container(horizontal=True):
        st.button("Restart", on_click=navigate)
        st.button("Previous", on_click=navigate, args=(-1,), disabled=state.position == 0)
        st.button("Pause" if state.playing else "Play", on_click=toggle, type="primary", disabled=state.position == len(state.events)-1)
        st.button("Next", on_click=navigate, args=(1,), disabled=state.position == len(state.events)-1)
    st.slider("Simulation step", 1, len(state.events), key="seek", on_change=seek)
    event = state.events[state.position]
    st.progress((state.position + 1) / len(state.events))
    with st.container(border=True):
        st.subheader("Final sorted array" if event["kind"] == "done" else event["kind"].capitalize())
        st.write(event["message"])
        st.caption(f"Step {state.position+1}/{len(state.events)} · Comparisons: {event['comparisons']} · Array writes: {event['writes']}")
        st.markdown("**Current array**")
        display_items(event["array"])
        node = event["nodes"][event["node_id"]]
        st.caption(f"Active range: [{node['lo']}, {node['hi']}) · # labels are original zero-based positions.")
    left_col, right_col = st.columns([3, 2])
    with left_col:
        st.subheader("Recursion tree")
        dot = ['digraph { rankdir=TB; node [shape=box];']
        for node in event["nodes"]:
            label = ", ".join(str(v) for v, _ in node["items"])
            dot.append(f'n{node["id"]} [label="[{node["lo"]}, {node["hi"]})\\n{label}\\n{node["state"]}" penwidth={3 if node["id"] == event["node_id"] else 1}];')
            if node["parent"] is not None:
                dot.append(f'n{node["parent"]} -> n{node["id"]};')
        dot.append('}')
        st.graphviz_chart("\n".join(dot), width="stretch")
    with right_col:
        st.subheader("Merge workspace")
        if "left" in event:
            for title, key, pointer in [("Left half", "left", event["i"]), ("Right half", "right", event["j"]), ("Temporary buffer", "buffer", None)]:
                st.markdown(f"**{title}**")
                display_items(event[key], pointer if event["kind"] == "compare" else None)
                if pointer is not None:
                    st.caption(f"Consumed {pointer}/{len(event[key])}")
        else:
            st.info("The workspace appears when both child ranges have been sorted.")
        st.code("""merge_sort(array):
    if length <= 1: return array
    split into left and right
    recursively sort both halves
    compare first remaining elements
    append smaller (left on ties)
    append remainder
    copy merged buffer back""", language="python")


simulator()
with st.expander("Complexity and stability", expanded=True):
    st.write("Time: O(n log n) in best, average, and worst cases. Each level does O(n) merging work across O(log n) levels.")
    st.write("Algorithm auxiliary space: O(n), plus an O(log n) recursion stack. The simulator additionally stores snapshots for backward navigation.")
    st.write("Stable: equal values choose the left element first. This buffer-based implementation is not in-place.")
    st.caption("Comparisons count value comparisons. Array writes count elements copied back after completed merges.")
with st.expander("Try these inputs"):
    st.code("5, 2, 5, 1, 2   # Stability\n-4, 0, -9, 2    # Negatives\n1, 2, 3, 4      # Already sorted\n9, 7, 5, 3, 1   # Reverse order\n42              # Base case", language="python")
st.caption("Original Python/Streamlit implementation for DAA coursework.")
