import re
import streamlit as st
import networkx as nx
from pyvis.network import Network

from build_graph import G, execute_query
from llm_pipeline import full_pipeline, generate_query

st.set_page_config(layout="wide")

ORDER_ID_PATTERN = r"SO_\d{6}_\d{2}"

def extract_order_ids(text: str):
    return re.findall(ORDER_ID_PATTERN, text.upper())

def is_trace_intent(text: str):
    text = text.lower()
    keywords = ["trace", "journey", "flow", "lifecycle", "path"]
    return any(k in text for k in keywords)

def build_trace_subgraph(graph, order_ids):
    nodes_to_show = set()
    for oid in order_ids:
        if oid in graph:
            nodes_to_show.add(oid)
            nodes_to_show.update(nx.descendants(graph, oid))
    if nodes_to_show:
        return graph.subgraph(nodes_to_show).copy(), nodes_to_show
    return None, set()

def get_node_color(node_type):
    return {
        "order": "#1f77b4",
        "delivery": "#ff7f0e",
        "invoice": "#2ca02c",
        "journal": "#d62728",
        "payment": "#9467bd"
    }.get(node_type, "#999999")

stage_order = ["order", "delivery", "invoice", "journal", "payment"]
level_map = {stage: i for i, stage in enumerate(stage_order)}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "trace_order_ids" not in st.session_state:
    st.session_state.trace_order_ids = []

if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

st.markdown("## 📊 Order to Cash — Graph Assistant")

col1, col2 = st.columns([3, 1])


trace_view = False
highlight_nodes = set()

if st.session_state.trace_order_ids:
    subgraph, highlight_nodes = build_trace_subgraph(G, st.session_state.trace_order_ids)
    if subgraph:
        trace_view = True
    else:
        subgraph = G.subgraph(list(G.nodes())[:200]).copy()
else:
    subgraph = G.subgraph(list(G.nodes())[:200]).copy()

with col1:
    st.markdown("### Graph")

    net = Network(height="700px", width="100%", directed=True)

    for node, data in subgraph.nodes(data=True):
        node_type = data.get("type", "default")
        color = get_node_color(node_type)

        label = node if trace_view else ""

        size = 22 if node in highlight_nodes else 10

        if node in st.session_state.trace_order_ids:
            color = "#FFD54F"
            size = 30

        net.add_node(
            node,
            label=label,
            title=str(data),
            color=color,
            size=size,
            level=level_map.get(node_type, 0)  
        )

    
    for u, v in subgraph.edges():

        if trace_view:
            net.add_edge(
                u, v,
                color="#ff0000",
                width=4,
                arrows="to"
            )
        else:
            net.add_edge(
                u, v,
                color="#9ec3eb",
                width=1,
                arrows="to"
            )

    
    if trace_view:
        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "LR",
              "sortMethod": "directed",
              "levelSeparation": 200,
              "nodeSpacing": 180,
              "treeSpacing": 250
            }
          },
          "physics": {
            "enabled": false
          },
          "edges": {
            "smooth": {
              "enabled": false
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 1.3
              }
            }
          },
          "nodes": {
            "font": {
              "size": 18
            }
          }
        }
        """)
    else:
        net.set_options("""
        {
          "physics": {
            "solver": "forceAtlas2Based",
            "stabilization": { "iterations": 120 }
          },
          "nodes": {
            "shape": "dot",
            "size": 10
          },
          "edges": {
            "smooth": true,
            "arrows": { "to": { "enabled": true } }
          }
        }
        """)

    html = net.generate_html()
    st.components.v1.html(html, height=700)

    
    st.markdown("""
    **Legend:**
    🔵 Order → 🟠 Delivery → 🟢 Invoice → 🔴 Journal → 🟣 Payment  
    🔥 Highlighted flow shows the traced business process
    """)

    
    if trace_view:
        st.success(f"Viewing Order(s): {', '.join(st.session_state.trace_order_ids)}")
        st.caption("Flow shows how the order progresses through the business lifecycle.")
    else:
        st.info("Enter a trace query to visualize the order lifecycle.")


with col2:
    st.markdown("### 🤖 Dodge AI")

    user_input = st.text_input("Analyze anything", value=st.session_state.last_user_input)

    if st.button("Reset Graph"):
        st.session_state.trace_order_ids = []
        st.rerun()

    if st.button("Send"):
        cleaned = user_input.strip()
        st.session_state.last_user_input = user_input

        if not cleaned:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Processing..."):

                structured_query = generate_query(cleaned)
                response = full_pipeline(cleaned, execute_query)

            ids = extract_order_ids(cleaned)

            if is_trace_intent(cleaned) and ids:
                st.session_state.trace_order_ids = ids
            else:
                st.session_state.trace_order_ids = []

            st.session_state.chat_history.append(("user", cleaned))
            st.session_state.chat_history.append(("debug", structured_query))
            st.session_state.chat_history.append(("bot", response))

            st.rerun()

    
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"🧑 **You:** {msg}")
        elif role == "debug":
            st.markdown(f"⚙️ **Query:** `{msg}`")
        else:
            st.markdown(f"🤖 **Dodge AI:** {msg}")
