from src.services.peer_review_engine import PeerReviewEngine

def main():
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

if __name__ == "__main__":
    main()