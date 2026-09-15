import os
import sys
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from agents.schemas import BatchSentimentResult

load_dotenv()

DB_PATH = ROOT_DIR / "data" / "sales.db"

def fetch_unanalyzed_reviews() -> list[dict]:
    """Veritabanında henüz sentiment analizi yapılmamış (IS NULL) yorumları getirir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT review_id, product_id, customer_name, review_text, review_date
        FROM reviews
        WHERE sentiment IS NULL
        ORDER BY review_id ASC;
    """)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "review_id": row[0],
            "product_id": row[1],
            "customer_name": row[2],
            "review_text": row[3],
            "review_date": row[4],
        }
        for row in rows
    ]

async def analyze_pending_reviews(batch_size: int = 10) -> BatchSentimentResult:
    """
    Fetches pending reviews and extracts structured sentiment using Gemini + Pydantic.
    """
    reviews = fetch_unanalyzed_reviews()
    if not reviews:
        return BatchSentimentResult(results=[])

    selected_reviews = reviews[:batch_size]

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Modeli toplu Pydantic şemamıza bağlıyoruz
    structured_llm = llm.with_structured_output(BatchSentimentResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior Product Quality & Customer Sentiment Analyst.
Analyze each customer review and return structured data according to the schema.

Guidelines:
1. 'sentiment': strictly 'positive', 'neutral', or 'negative'.
2. 'issue_type': identify the core topic/flaw (e.g. 'battery', 'build_quality', 'connectivity', 'packaging', 'none').
3. 'flagged_for_ops': Set to True ONLY if there is a severe defect, rapid failure, safety concern, or recurring flaw (e.g. battery draining in 30 mins, broken components).
4. 'reason': A concise single-sentence business justification.
"""),
        ("human", "Analyze the following batch of customer reviews:\n\n{reviews_json}")
    ])

    formatted_prompt = prompt.format_messages(
        reviews_json=json.dumps(selected_reviews, indent=2, ensure_ascii=False)
    )

    result: BatchSentimentResult = await structured_llm.ainvoke(formatted_prompt)
    return result

if __name__ == "__main__":
    import asyncio

    async def main():
        print("Bekleyen yorumlar getiriliyor ve Gemini ile analiz ediliyor...")
        batch_result = await analyze_pending_reviews(batch_size=10)
        
        print(f"\nToplam Analiz Edilen Yorum: {len(batch_result.results)}\n")
        for item in batch_result.results:
            flag_str = " [FLAGGED FOR OPS]" if item.flagged_for_ops else ""
            print(f"- [Review #{item.review_id}] {item.sentiment.upper()} (Güven: {item.confidence:.2f}) | Kategori: {item.issue_type}{flag_str}")
            print(f"  Gerekçe: {item.reason}")

    asyncio.run(main())