import sqlite3
import asyncio
from pathlib import Path
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="E-Commerce AI Agent & BI Analytics",
    page_icon="📊",
    layout="wide"
)

DB_PATH = Path(__file__).resolve().parent / "data" / "sales.db"
SQL_DIR = Path(__file__).resolve().parent / "sql"

# Database Helper Functions
def get_db_connection():
    return sqlite3.connect(DB_PATH)

def run_sql_file(file_name: str) -> pd.DataFrame:
    sql_path = SQL_DIR / file_name
    if not sql_path.exists():
        return pd.DataFrame()
    with open(sql_path, "r", encoding="utf-8") as f:
        query = f.read()
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def execute_async(coro):
    """Executes async coroutine safely inside Streamlit's runtime."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.caption("E-Commerce Multi-Agent Platform")
    
    if st.button("🔄 Reset / Seed Database", use_container_width=True):
        import subprocess
        import sys
        
        # data/seed.py dosyasını temiz bir alt süreç olarak çalıştır
        seed_script = Path(__file__).resolve().parent / "data" / "seed.py"
        subprocess.run([sys.executable, str(seed_script)], check=True)
        
        st.session_state.clear()
        st.success("Database successfully reset and re-seeded!")
        st.rerun()
    
    st.markdown("---")
    st.subheader("Database Metrics")
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        total_sales = c.execute("SELECT SUM(revenue) FROM sales;").fetchone()[0] or 0
        total_reviews = c.execute("SELECT COUNT(*) FROM reviews;").fetchone()[0] or 0
        pending_reviews = c.execute("SELECT COUNT(*) FROM reviews WHERE sentiment IS NULL;").fetchone()[0] or 0
        conn.close()
        
        st.metric("Total Revenue", f"${total_sales:,.2f}")
        st.metric("Total Reviews", total_reviews)
        st.metric("Unanalyzed Reviews", pending_reviews)
    except Exception as e:
        st.error(f"DB Error: {e}")

# ----------------- MAIN INTERFACE -----------------
st.title("📊 E-Commerce Sales & Sentiment Intelligence")
st.markdown(
    "Decision intelligence engine combining **Analytical SQL Models**, autonomous **Multi-Agent Orchestration**, "
    "and **Human-in-the-Loop (HITL)** governance before committing data mutations."
)

tab_bi, tab_agent = st.tabs(["📈 BI & Analytical SQL Models", "🤖 Multi-Agent Orchestration & HITL"])

# --- TAB 1: BI & ANALYTICAL SQL MODELS ---
with tab_bi:
    st.subheader("1. Weekly Revenue Trends & WoW Performance (`01_weekly_revenue_trend.sql`)")
    df_revenue = run_sql_file("01_weekly_revenue_trend.sql")
    
    if not df_revenue.empty:
        col_table, col_chart = st.columns([1, 1])
        with col_table:
            st.dataframe(df_revenue, use_container_width=True, height=280)
        with col_chart:
            pivot_revenue = df_revenue.pivot(
                index="week_start_date", columns="product_name", values="revenue"
            )
            st.line_chart(pivot_revenue)
    else:
        st.info("No revenue trend records found in database.")

    st.markdown("---")
    st.subheader("2. Customer Feedback & Issue Clustering (`02_sentiment_summary.sql`)")
    st.caption("Aggregated defect clusters per product powered by `GROUP_CONCAT(DISTINCT ...)`:")
    df_sentiment = run_sql_file("02_sentiment_summary.sql")
    
    if not df_sentiment.empty:
        st.dataframe(df_sentiment, use_container_width=True)
    else:
        st.info("No analyzed reviews found yet. Run the Sentiment Agent to populate analytical sentiment data.")

# --- TAB 2: MULTI-AGENT ORCHESTRATION & HITL ---
with tab_agent:
    st.subheader("Natural Language Business & Operational Query")
    
    # Initialize Session State
    if "graph" not in st.session_state:
        from agents.graph_flow import build_ecommerce_graph
        st.session_state.graph = build_ecommerce_graph()
        st.session_state.config = {"configurable": {"thread_id": "streamlit-session-ui"}}
        st.session_state.pending_data = None
        st.session_state.interrupt_msg = None
        st.session_state.final_summary = None

    default_query = "Which product has the highest total revenue but suffers from deteriorating customer reviews?"
    user_query = st.text_input("Analytical Prompt / Business Question:", value=default_query)

    if st.button("🚀 Execute Autonomous Agents", type="primary"):
        st.session_state.pending_data = None
        st.session_state.final_summary = None
        
        with st.spinner("Agents querying SQLite via MCP and performing structured extraction..."):
            execute_async(st.session_state.graph.ainvoke(
                {"user_query": user_query},
                config=st.session_state.config
            ))
            
            snapshot = st.session_state.graph.get_state(st.session_state.config)
            
            if snapshot.next:
                # Human-in-the-Loop Interrupt State
                tasks = snapshot.tasks
                if tasks and tasks[0].interrupts:
                    details = tasks[0].interrupts[0].value
                    st.session_state.interrupt_msg = details.get("message")
                    st.session_state.pending_data = details.get("pending_data", [])
            else:
                st.session_state.final_summary = snapshot.values.get("final_summary")

    # Human-in-the-Loop Approval Card
    if st.session_state.pending_data:
        from langgraph.types import Command
        
        st.warning("⚠️ **Human-in-the-Loop Interruption:** Database write permissions withheld pending human authorization.")
        if st.session_state.interrupt_msg:
            st.info(st.session_state.interrupt_msg)
        
        df_pending = pd.DataFrame(st.session_state.pending_data)
        st.dataframe(
            df_pending[["review_id", "sentiment", "issue_type", "flagged_for_ops", "reason"]],
            use_container_width=True
        )

        col_app, col_rej = st.columns([1, 1])
        with col_app:
            if st.button("✅ Authorize & Commit Updates to SQLite", type="primary", use_container_width=True):
                with st.spinner("Authorizing transaction and compiling executive summary..."):
                    res = execute_async(st.session_state.graph.ainvoke(
                        Command(resume={"approved": True}),
                        config=st.session_state.config
                    ))
                    st.session_state.final_summary = res.get("final_summary")
                    st.session_state.pending_data = None
                    st.success("Analysis results successfully committed to the database!")
                    st.rerun()

        with col_rej:
            if st.button("❌ Reject (Discard DB Mutations)", use_container_width=True):
                with st.spinner("Discarding pending updates..."):
                    res = execute_async(st.session_state.graph.ainvoke(
                        Command(resume={"approved": False}),
                        config=st.session_state.config
                    ))
                    st.session_state.final_summary = res.get("final_summary")
                    st.session_state.pending_data = None
                    st.info("Database updates rejected. No changes committed.")
                    st.rerun()

    # Executive Summary Output
    if st.session_state.final_summary:
        st.markdown("---")
        st.subheader("📋 Executive Summary Report")
        st.markdown(st.session_state.final_summary)