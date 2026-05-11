from fastapi import APIRouter
from src.services.peer_review_engine import PeerReviewEngine

router = APIRouter(prefix="/students", tags=["Students"])

engine = PeerReviewEngine(
    "data/processed/students_clean.csv",
    "data/processed/works_clean.csv",
    "data/processed/reviews_clean.csv"
)

@router.get("/")
def get_students():
    data = engine.students.copy()

    if "first_name" in data.columns and "last_name" in data.columns:
        data["name"] = data["first_name"] + " " + data["last_name"]

    data["level"] = "N/A"

    return data.fillna("").to_dict(orient="records")