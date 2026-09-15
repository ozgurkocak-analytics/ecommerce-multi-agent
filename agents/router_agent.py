import os
import sys
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv()

class RouteDecision(BaseModel):
    """Kullanıcı sorgusunun yönlendirileceği ajanı ve gerekçesini belirten şema."""
    destination: Literal["sql", "sentiment", "both"] = Field(
        description="Select 'sql' for purely numerical/sales/revenue questions, "
                    "'sentiment' for customer feedback/review topics, "
                    "or 'both' for questions comparing financial performance with customer sentiment."
    )
    reason: str = Field(
        description="Brief reasoning for choosing this destination."
    )

def create_router_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    return llm.with_structured_output(RouteDecision)

async def route_user_query(query: str) -> RouteDecision:
    """Kullanıcının doğal dil sorgusunu sınıflandırır."""
    router = create_router_agent()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a smart query router in an e-commerce intelligence system.
Your job is to analyze the user's prompt and route it to the appropriate sub-agent(s):
- 'sql': Only sales, revenue, quantity, dates, pricing, or product catalog numbers.
- 'sentiment': Only customer opinions, complaints, defects, satisfaction, or review text.
- 'both': Questions that require combining financial/sales metrics with customer feedback or root-cause explanations.
"""),
        ("human", "{query}")
    ])
    
    return await router.ainvoke(prompt.format_messages(query=query))

if __name__ == "__main__":
    import asyncio

    async def test_routing():
        test_queries = [
            "Hangi ürünün toplam geliri en yüksek?",
            "Müşteriler en çok hangi konularda şikayet yazmış?",
            "Hangi ürünün cirosu yüksek olduğu halde müşteri yorumları kötü gidiyor?"
        ]
        
        print("Router Ajanı Test Ediliyor...\n")
        for q in test_queries:
            decision = await route_user_query(q)
            print(f"Soru: '{q}'")
            print(f"-> Hedef: [{decision.destination.upper()}] | Gerekçe: {decision.reason}\n")

    asyncio.run(test_routing())