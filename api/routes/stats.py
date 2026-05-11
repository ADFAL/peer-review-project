from fastapi import APIRouter
from src.services.peer_review_engine import PeerReviewEngine

router = APIRouter(prefix="/stats", tags=["Stats"])

engine = PeerReviewEngine(
    "data/processed/students_clean.csv",
    "data/processed/works_clean.csv",
    "data/processed/reviews_clean.csv"
)

@router.get("/")
def stats():
    return {
        "students": len(engine.students),
        "works": len(engine.works),
        "reviews": len(engine.reviews),
        "avg_note": float(engine.reviews["note"].mean()) if "note" in engine.reviews else 0
    }