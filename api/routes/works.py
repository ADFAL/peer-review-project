from fastapi import APIRouter
from src.services.peer_review_engine import PeerReviewEngine

router = APIRouter(prefix="/works", tags=["Works"])

engine = PeerReviewEngine(
    "data/processed/students_clean.csv",
    "data/processed/works_clean.csv",
    "data/processed/reviews_clean.csv"
)

@router.get("/")
def get_works():
    data = engine.works.copy()

    data["title"] = data.get("title", "")
    data["description"] = data.get("description", "")
    data["student_id"] = data.get("student_id", "")

    return data.fillna("").to_dict(orient="records")