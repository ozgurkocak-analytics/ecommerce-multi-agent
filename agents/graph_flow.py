import os
import sys
from typing import TypedDict, Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from agents.router_agent import route_user_query
from agents.sql_agent import run_sql_query_agent
from agents.sentiment_agent import analyze_pending_reviews
from agents.schemas import SentimentAnalysisResult
from agents.db_ops import apply_sentiment_updates
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Graf Durumu (State) Tanımı
class AgentState(TypedDict):
    user_query: str
    route: str
    sql_result: Optional[str]
    pending_updates: Optional[List[Dict[str, Any]]]
    human_approved: Optional[bool]
    db_updated_count: int
    final_summary: Optional[str]

# 1. Düğüm: Yönlendirme
async def node_route(state: AgentState) -> Dict[str, Any]:
    decision = await route_user_query(state["user_query"])
    return {"route": decision.destination}

# 2. Düğüm: SQL Analizi
async def node_sql(state: AgentState) -> Dict[str, Any]:
    ans = await run_sql_query_agent(state["user_query"])
    return {"sql_result": ans}

# 3. Node: Sentiment Analysis
async def node_sentiment(state: AgentState) -> Dict[str, Any]:
    batch = await analyze_pending_reviews(batch_size=10)
    updates = [item.model_dump() for item in batch.results]
    return {"pending_updates": updates}

# 4. Node: Human Approval (Human-in-the-Loop Interrupt)
def node_human_approval(state: AgentState) -> Dict[str, Any]:
    pending = state.get("pending_updates", [])
    if not pending:
        return {"human_approved": True, "db_updated_count": 0}
    
    approval_response = interrupt({
        "message": f"{len(pending)} pending review analysis results are awaiting human approval before DB commit.",
        "pending_data": pending
    })
    
    is_approved = bool(approval_response.get("approved", False)) if isinstance(approval_response, dict) else bool(approval_response)
    return {"human_approved": is_approved}

# 5. Düğüm: Veritabanına Yazma
def node_commit(state: AgentState) -> Dict[str, Any]:
    if state.get("human_approved"):
        raw_items = state.get("pending_updates") or []
        items = [SentimentAnalysisResult(**x) for x in raw_items]
        count = apply_sentiment_updates(items)
        return {"db_updated_count": count}
    return {"db_updated_count": 0}

# 6. Düğüm: Nihai Özet (Summary Agent)
async def node_summary(state: AgentState) -> Dict[str, Any]:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Lead E-Commerce Business & Intelligence Analyst.
Synthesize the technical findings into a concise, professional executive answer.
Cite numbers clearly. If operational issues (like battery defects) were identified, highlight the root cause and business impact."""),
        ("human", """User Question: {query}
SQL Analytics Result: {sql_res}
Sentiment Updates Count: {updates_count}
Flagged Sentiment Summary: {sentiment_summary}
""")
    ])
    
    flagged = [p for p in (state.get("pending_updates") or []) if p.get("flagged_for_ops")]
    summary_text = f"Analyzed {len(state.get('pending_updates') or [])} reviews, flagged {len(flagged)} critical operational defects."

    res = await llm.ainvoke(prompt.format_messages(
        query=state["user_query"],
        sql_res=state.get("sql_result") or "N/A",
        updates_count=state.get("db_updated_count", 0),
        sentiment_summary=summary_text
    ))
    
    content = "".join(part.get("text", "") for part in res.content) if isinstance(res.content, list) else str(res.content)
    return {"final_summary": content}

# Grafiği Oluşturma ve Bağlama
def build_ecommerce_graph():
    builder = StateGraph(AgentState)

    builder.add_node("router", node_route)
    builder.add_node("sql_agent", node_sql)
    builder.add_node("sentiment_agent", node_sentiment)
    builder.add_node("human_review", node_human_approval)
    builder.add_node("commit_db", node_commit)
    builder.add_node("summary_agent", node_summary)

    # Başlangıç
    builder.add_edge(START, "router")

    # Koşullu Yönlendirme Mantığı
    def route_condition(state: AgentState) -> str:
        r = state["route"]
        if r == "sql":
            return "sql_agent"
        elif r == "sentiment":
            return "sentiment_agent"
        else:
            return "both"

    # Router dallanması
    builder.add_conditional_edges(
        "router",
        route_condition,
        {
            "sql_agent": "sql_agent",
            "sentiment_agent": "sentiment_agent",
            "both": "sql_agent"
        }
    )

    # 'both' senaryosunda sql_agent'tan sonra sentiment_agent'a geçiş
    def after_sql_condition(state: AgentState) -> str:
        return "sentiment_agent" if state["route"] == "both" else "summary_agent"

    builder.add_conditional_edges(
        "sql_agent",
        after_sql_condition,
        {
            "sentiment_agent": "sentiment_agent",
            "summary_agent": "summary_agent"
        }
    )

    # Sentiment sonrasında mutlaka insan onayına git
    builder.add_edge("sentiment_agent", "human_review")
    builder.add_edge("human_review", "commit_db")
    builder.add_edge("commit_db", "summary_agent")
    builder.add_edge("summary_agent", END)

    # Human-in-the-loop için hafıza tutucu (checkpointer) şarttır
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)