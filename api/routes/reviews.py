from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/reviews", tags=["Reviews"])

reviews = pd.read_csv("data/processed/reviews_clean.csv")

@router.get("/")
def get_reviews(limit: int = 1000):
    return reviews.head(limit).fillna("").to_dict(orient="records")