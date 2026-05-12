from fastapi import APIRouter, Query
from src.services.peer_review_engine import PeerReviewEngine
from src.models.model import Model

router = APIRouter(prefix="/stats", tags=["Stats"])

engine = PeerReviewEngine(
    "data/processed/students_clean.csv",
    "data/processed/works_clean.csv",
    "data/processed/reviews_clean.csv"
)

# Load AI model once
model = Model(reviews_df=engine.reviews, works_df=engine.works)

# ── Existing endpoint ──────────────────────
@router.get("/")
def stats():
    return {
        "students": len(engine.students),
        "works":    len(engine.works),
        "reviews":  len(engine.reviews),
        "avg_note": float(engine.reviews["note"].mean()) if "note" in engine.reviews else 0
    }

# ══════════════════════════════════════════
# 🤖 AI MODEL ENDPOINTS
# ══════════════════════════════════════════

@router.get("/classify-works")
def classify_works():
    """Classifie les travaux : Excellent / Moyen / Faible"""
    df = model.classify_all_works()
    return df.to_dict(orient="records")


@router.get("/similar-works/{work_id}")
def similar_works(work_id: int, top_n: int = 3):
    """Trouve les travaux similaires via TF-IDF + Cosine Similarity"""
    return model.find_similar_works(work_id, top_n=top_n)


@router.get("/biased-reviewers")
def biased_reviewers(threshold: float = Query(default=3.0)):
    """Détecte les reviewers biaisés"""
    df = model.detect_all_biased_reviewers(threshold=threshold)
    if df.empty:
        return []
    return df.to_dict(orient="records")