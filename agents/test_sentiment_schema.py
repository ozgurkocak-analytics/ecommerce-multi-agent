import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from schemas import SentimentAnalysisResult

load_dotenv()

def test_single_review_analysis():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0.0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # Modeli Pydantic semamiza zorluyoruz
    structured_llm = llm.with_structured_output(SentimentAnalysisResult)

    sample_review = (
        "Battery drops from 100% to zero in less than 30 minutes! Unacceptable."
    )

    prompt = f"""
    Analyze the following customer review and extract structured information.
    Review ID: 101
    Review Text: "{sample_review}"
    """

    print("Gemini modeline analiz istegi gonderiliyor...")
    result: SentimentAnalysisResult = structured_llm.invoke(prompt)

    print("\n--- Modelin Yapilandirilmis Ciktisi ---")
    print(f"Review ID: {result.review_id}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Confidence: {result.confidence}")
    print(f"Issue Type: {result.issue_type}")
    print(f"Flagged for Ops: {result.flagged_for_ops}")
    print(f"Reason: {result.reason}")

if __name__ == "__main__":
    test_single_review_analysis()