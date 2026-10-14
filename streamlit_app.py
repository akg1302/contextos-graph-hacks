from __future__ import annotations

import uuid

from dotenv import load_dotenv

# Load configuration before importing modules that read environment variables.
load_dotenv()

import streamlit as st

from app.agent import answer_question
from app.graph_store import get_graph, graph_overview, recent_memories, seed_demo_graph
st.set_page_config(page_title="ContextOS | Company Brain", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 1.35rem 1.5rem; border: 1px solid rgba(120,140,180,.25); border-radius: 18px; background: linear-gradient(120deg, rgba(35,55,90,.35), rgba(35,100,110,.15));}
.small-muted {color: #8b95a7; font-size: .9rem;}
</style>
<div class="hero">
  <h1>🧠 ContextOS</h1>
  <p><b>Evidence-first Company Brain</b> · Powered by FalkorDB</p>
  <p class="small-muted">Connected knowledge • Persistent memory • Traceable decisions</p>
</div>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    graph = get_graph()
    # First-run experience: seed the synthetic graph automatically when this graph is empty.
    # The sidebar still exposes a repair/reseed control for the demo.
    initial_overview = graph_overview(graph)
    if not initial_overview["nodes"]:
        seed_demo_graph(graph)
    st.sidebar.success("FalkorDB connected · graph ready")
except Exception as exc:
    st.error("ContextOS database start nahi kar paaya. Replit ke Build/Console panel mein startup error check karein.")
    st.code("Default: embedded FalkorDBLite (no Docker/cloud credentials)\nCloud mode is optional and requires a healthy managed instance.")
    st.caption("Credentials ko chat mein share mat karna. Technical detail: " + str(exc))
    st.stop()

with st.sidebar:
    st.subheader("Demo controls")
    if st.button("🌱 Seed / repair synthetic demo graph", use_container_width=True):
        try:
            counts = seed_demo_graph(graph)
            st.success("Graph ready: " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
        except Exception as exc:
            st.error(f"Graph seed failed: {exc}")
    if st.button("♻️ Reset and reseed graph", use_container_width=True):
        try:
            counts = seed_demo_graph(graph, reset=True)
            st.success("Graph reset. " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
        except Exception as exc:
            st.error(f"Graph reset failed: {exc}")
    st.divider()
    st.write("**Current session**")
    st.code(st.session_state.session_id)
    if st.button("Start a new session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()
    st.caption("Memory graph mein save hoti hai, isliye new session start karne ke baad bhi history survive karti hai.")

# The seed action is explicit to avoid silently mutating the user's database.
try:
    overview = graph_overview(graph)
    total_nodes = sum(item["count"] for item in overview["nodes"])
    total_edges = sum(item["count"] for item in overview["relationships"])
except Exception:
    total_nodes, total_edges = 0, 0

m1, m2, m3 = st.columns(3)
m1.metric("Graph node types", len(overview["nodes"]) if 'overview' in locals() else 0)
m2.metric("Graph nodes", total_nodes)
m3.metric("Relationship types shown", len(overview["relationships"]) if 'overview' in locals() else 0)

st.subheader("Ask the company brain")
st.write("Synthetic incident-response workspace. Answers are grounded in FalkorDB traversals and include evidence paths retrieved from the graph.")
examples = [
    "Why is checkout failing, and who should investigate?",
    "Have we seen a similar incident before? What did we decide?",
    "Which services may be affected if Payment Gateway has problems?",
    "Which runbook should the on-call engineer use?",
]
cols = st.columns(2)
for i, example in enumerate(examples):
    if cols[i % 2].button(example, use_container_width=True, key=f"example_{i}"):
        st.session_state.pending_question = example

question = st.chat_input("Ask about an incident, owner, past decision, or runbook...")
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("FalkorDB graph paths traverse kar raha hai..."):
            try:
                output = answer_question(graph, st.session_state.session_id, question)
                st.markdown(output["answer"])
                with st.expander("🔎 Evidence & graph paths", expanded=True):
                    analysis = output["analysis"]
                    if analysis.get("incident"):
                        st.write("**Current incident**", analysis["incident"])
                        st.write("**Services found through graph**", analysis["services"])
                        st.write("**Owners**", analysis["owners"])
                        st.write("**On-call contacts**", analysis["on_call"])
                        st.write("**Runbooks**", analysis["runbooks"])
                        st.write("**Impacted upstream services**", analysis["impacted_services"])
                        st.write("**Evidence paths**")
                        for item in analysis["evidence"]:
                            st.markdown(f"- `{item['path']}` — {item['why']}")
                    else:
                        st.info("No matching incident. Sidebar se synthetic demo graph seed karo.")
                st.session_state.messages.append({"role": "assistant", "content": output["answer"]})
            except Exception as exc:
                st.error(f"Query run nahi hui: {exc}")

st.divider()
left, right = st.columns([1.1, 1])
with left:
    st.subheader("Graph topology snapshot")
    if overview["nodes"]:
        st.dataframe(overview["nodes"], use_container_width=True, hide_index=True)
    else:
        st.info("Abhi graph empty hai. Sidebar se seed karo.")
with right:
    st.subheader("Relationship types")
    if overview["relationships"]:
        st.dataframe(overview["relationships"], use_container_width=True, hide_index=True)
    else:
        st.info("Relationships appear after seeding.")

st.subheader("Persistent episodic memory")
try:
    memories = recent_memories(graph, limit=10)
    if memories:
        for memory in memories:
            with st.expander(f"{memory['question'][:100]} · session {memory['session']}"):
                st.write(memory["answer"])
                st.caption(f"Stored timestamp: {memory['created_at']}")
    else:
        st.caption("Abhi tak koi question memory mein save nahi hua. Ek question pooch kar test karo.")
except Exception as exc:
    st.warning(f"Memory list load nahi hui: {exc}")

st.caption("Synthetic demo data only · Recommendations are advisory · No production action is executed.")
