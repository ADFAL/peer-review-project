from fastapi import APIRouter
from src.services.peer_review_engine import PeerReviewEngine

router = APIRouter(prefix="/ranking", tags=["Ranking"])

engine = PeerReviewEngine(
    "data/processed/students_clean.csv",
    "data/processed/works_clean.csv",
    "data/processed/reviews_clean.csv"
)

@router.get("/students")
def student_ranking():
    return engine.student_ranking().fillna("").to_dict(orient="records")

@router.get("/works")
def work_ranking():
    return engine.work_ranking().fillna("").to_dict(orient="records")