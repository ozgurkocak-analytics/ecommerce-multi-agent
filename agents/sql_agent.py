import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Proje ana dizinini Python yoluna ekle
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from agents.mcp_client import get_sqlite_mcp_tools

load_dotenv()

SQL_AGENT_SYSTEM_PROMPT = """You are a specialized SQL Data Analyst for an e-commerce platform.
Your job is to answer analytical and financial questions strictly by querying the SQLite database using the provided MCP tools.

Database Schema Context:
- products(product_id, product_name, category, launch_date, unit_price)
- sales(sale_id, product_id, week_start_date, units_sold, revenue)
- reviews(review_id, product_id, customer_name, review_text, review_date, sentiment, issue_type, flagged_for_ops)

Rules:
1. Always use 'read_query' to fetch data. NEVER guess numbers or metrics.
2. Read-only: DO NOT execute INSERT, UPDATE, or DELETE statements.
3. Write standard SQLite queries. For trends or WoW growth, you may use window functions like LAG().
4. Answer concisely with clear numbers, product names, and dates.
"""

async def create_sql_agent():
    tools = await get_sqlite_mcp_tools()
    
    # Yalnızca sorgulama ve şema okuma araçlarını filtreleyelim (güvenlik için)
    read_tools = [t for t in tools if t.name in ["read_query", "list_tables", "describe_table"]]
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Modeli araçlarla donatıyoruz
    llm_with_tools = llm.bind_tools(read_tools)
    return llm_with_tools, read_tools

async def run_sql_query_agent(question: str) -> str:
    """Verilen sayısal veya analitik soruyu MCP araçları üzerinden yanıtlar."""
    llm_with_tools, tools_list = await create_sql_agent()
    tool_map = {t.name: t for t in tools_list}
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SQL_AGENT_SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    
    messages = prompt.format_messages(question=question)
    response = await llm_with_tools.ainvoke(messages)
    
    # Eğer model bir araç çağırmak istediyse (tool_calls)
    while response.tool_calls:
        messages.append(response)
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            selected_tool = tool_map.get(tool_name)
            
            if selected_tool:
                tool_output = await selected_tool.ainvoke(tool_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "content": str(tool_output)
                })
        
        # Aracın çıktısını modele geri verip nihai yanıtı alıyoruz
        response = await llm_with_tools.ainvoke(messages)
        
    # Yanıtı temiz metin olarak döndür
    if isinstance(response.content, list):
        return "".join(part.get("text", "") for part in response.content if isinstance(part, dict))
    return str(response.content)

if __name__ == "__main__":
    import asyncio
    
    async def test():
        test_q = "Hangi ürün toplamda en yüksek geliri sağladı ve haftalık ortalama satışı ne kadar?"
        print(f"Soru: {test_q}\n")
        answer = await run_sql_query_agent(test_q)
        print(f"SQL Ajanı Yanıtı:\n{answer}")
        
    asyncio.run(test())