import pandas as pd
from src.services.peer_review_engine import PeerReviewEngine
from src.models.model import Model


def main():
    # =====================
    # PeerReviewEngine
    # =====================
    engine = PeerReviewEngine(
        "data/processed/students_clean.csv",
        "data/processed/works_clean.csv",
        "data/processed/reviews_clean.csv",
    )

    print("👤 Students preview:")
    print(engine.students.head())

    print("\n📄 Works preview:")
    print(engine.works.head())

    print("\n⭐ Reviews preview:")
    print(engine.reviews.head())

    print("\n🏆 Work ranking:")
    print(engine.work_ranking())

    print("\n👤 Student ranking:")
    print(engine.student_ranking())

    # =====================
    # AI Model
    # =====================
    print("\n" + "="*50)
    print("🤖 AI Model — Peer Review")
    print("="*50)

    model = Model(
        reviews_df=engine.reviews,
        works_df=engine.works,
    )

    # 1. Classify all works
    print("\n📊 Classification des travaux :")
    print(model.classify_all_works())

    # 2. Find similar works (first work_id)
    first_work_id = engine.reviews["work_id"].iloc[0]
    print(f"\n🔍 Travaux similaires à work_id={first_work_id} :")
    print(model.find_similar_works(first_work_id))

    # 3. Detect biased reviewers
    print("\n⚠️ Reviewers biaisés :")
    biased = model.detect_all_biased_reviewers()
    print(biased if not biased.empty else "Aucun reviewer biaisé détecté.")

    # 4. Save model
    model.save("models/peer_review_model.joblib")
    print("\n✅ Model sauvegardé avec succès!")


if __name__ == "__main__":
    main()