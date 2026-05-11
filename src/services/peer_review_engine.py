import pandas as pd

class PeerReviewEngine:
    def __init__(self, students_path, works_path, reviews_path):

        self.students = pd.read_csv(students_path)
        self.works = pd.read_csv(works_path)
        self.reviews = pd.read_csv(reviews_path)

        self.students.columns = self.students.columns.str.strip().str.lower()
        self.works.columns = self.works.columns.str.strip().str.lower()
        self.reviews.columns = self.reviews.columns.str.strip().str.lower()

    # =====================
    # 🏆 WORK RANKING
    # =====================
    def work_ranking(self):
        if "work_id" not in self.reviews.columns:
            return pd.DataFrame()

        ranking = self.reviews.groupby("work_id")["note"].mean().reset_index()
        return ranking.sort_values("note", ascending=False)

    # =====================
    # 👤 STUDENT RANKING
    # =====================
    def student_ranking(self):

        # merge works with reviews to get student_id
        merged = self.reviews.merge(
            self.works,
            left_on="work_id",
            right_on="id",
            how="left"
        )

        if "student_id" not in merged.columns:
            return pd.DataFrame()

        ranking = merged.groupby("student_id")["note"].mean().reset_index()

        return ranking.sort_values("note", ascending=False)