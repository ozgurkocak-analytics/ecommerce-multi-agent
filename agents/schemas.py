from typing import Literal, Optional
from pydantic import BaseModel, Field


class SentimentAnalysisResult(BaseModel):
    """Tek bir müşteri yorumunun yapılandırılmış analiz çıktısı."""

    review_id: int = Field(
        description="Analiz edilen yorumun veritabanındaki benzersiz kimliği (review_id)"
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="Yorumun duygu durumu"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Duygu analizi tahmininin 0.0 ile 1.0 arasındaki güven skoru",
    )
    issue_type: str = Field(
        default="none",
        description="Tespit edilen ana problem teması (örn: 'battery', 'connectivity', 'audio_quality', 'none')",
    )
    flagged_for_ops: bool = Field(
        description="Kritik/kronik bir kusur nedeniyle operasyon ekibine eskalasyon gerekiyor mu (True/False)"
    )
    reason: str = Field(
        description="Bu sınıflandırma ve bayraklamanın kısa iş gerekçesi (1 cümle)"
    )


class BatchSentimentResult(BaseModel):
    """Birden fazla yorumun toplu analiz çıktısı."""

    results: list[SentimentAnalysisResult] = Field(
        description="Analiz edilen yorumların listesi"
    )