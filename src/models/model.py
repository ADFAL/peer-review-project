import pandas as pd
import numpy as np
import joblib
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


class Model:
    """
    Peer Review AI Model
    ---------------------
    Basé sur scikit-learn :

    1. classify_work()        → Classifie un travail : Excellent / Moyen / Faible
                                (MinMaxScaler + seuillage)

    2. find_similar_works()   → Trouve les travaux similaires via TF-IDF + Cosine Similarity
                                (sur les commentaires des reviews)

    3. detect_biased_reviewer() → Détecte les reviewers biaisés
                                  (écart important par rapport à la moyenne globale)

    4. save() / load()        → Sauvegarde et rechargement du modèle (joblib)
    """

    def __init__(self, reviews_df: pd.DataFrame, works_df: pd.DataFrame):
        self.reviews = reviews_df.copy()
        self.works   = works_df.copy()

        # Normalize column names
        self.reviews.columns = self.reviews.columns.str.strip().str.lower()
        self.works.columns   = self.works.columns.str.strip().str.lower()

        # Internal components (scikit-learn)
        self.vectorizer    = TfidfVectorizer(stop_words="english", max_features=100)
        self.scaler        = MinMaxScaler(feature_range=(0, 20))
        self.tfidf_matrix  = None
        self.work_ids      = None

        # Auto-train on init
        self._train()

    # =====================================================
    # TRAINING
    # =====================================================
    def _train(self):
        """Entraîne le vectoriseur TF-IDF sur les commentaires."""
        if "comment" not in self.reviews.columns or self.reviews.empty:
            return

        # Group comments by work_id
        # Sample for performance on large datasets
        sample = self.reviews.sample(n=min(len(self.reviews), 5000), random_state=42)
        work_comments = (
            sample.groupby("work_id")["comment"]
            .apply(lambda x: " ".join(x.dropna().astype(str)))
            .reset_index()
        ).head(1000)

        if work_comments.empty:
            return

        self.work_ids     = work_comments["work_id"].tolist()
        self.tfidf_matrix = self.vectorizer.fit_transform(work_comments["comment"])

    # =====================================================
    # 1. CLASSIFICATION DU TRAVAIL
    # =====================================================
    def classify_work(self, work_id: int) -> dict:
        """
        Classifie un travail selon la moyenne de ses notes.
        Utilise MinMaxScaler pour normaliser les notes sur [0, 20].
          - Excellent : note >= 14
          - Moyen     : 10 <= note < 14
          - Faible    : note < 10
        """
        work_reviews = self.reviews[self.reviews["work_id"] == work_id]["note"]

        if work_reviews.empty:
            return {"work_id": work_id, "classification": "No reviews yet", "average": None}

        # Scale notes using MinMaxScaler
        all_notes = self.reviews["note"].values.reshape(-1, 1)
        self.scaler.fit(all_notes)
        scaled = self.scaler.transform(work_reviews.values.reshape(-1, 1)).flatten()

        average = round(float(scaled.mean()), 2)

        if average >= 14:
            classification = "Excellent"
        elif average >= 10:
            classification = "Moyen"
        else:
            classification = "Faible"

        return {
            "work_id":        work_id,
            "average":        average,
            "classification": classification,
            "num_reviews":    int(work_reviews.count()),
        }

    def classify_all_works(self) -> pd.DataFrame:
        """Classifie les 500 premiers travaux disponibles."""
        work_ids = self.reviews["work_id"].unique()[:500]
        results = []
        for work_id in work_ids:
            results.append(self.classify_work(work_id))
        df = pd.DataFrame(results).dropna(subset=["average"])
        return df.sort_values("average", ascending=False).reset_index(drop=True)

    # =====================================================
    # 2. SIMILARITÉ DES TRAVAUX (TF-IDF + Cosine Similarity)
    # =====================================================
    def find_similar_works(self, work_id: int, top_n: int = 3) -> dict:
        """
        Trouve les travaux les plus similaires à un travail donné,
        en comparant les commentaires via TF-IDF + Cosine Similarity.
        """
        if self.tfidf_matrix is None or self.work_ids is None:
            return {"work_id": work_id, "similar_works": [], "message": "Model not trained"}

        if work_id not in self.work_ids:
            return {"work_id": work_id, "similar_works": [], "message": "Work not found"}

        idx = self.work_ids.index(work_id)

        # Compute cosine similarity
        similarity_scores = cosine_similarity(
            self.tfidf_matrix[idx],
            self.tfidf_matrix
        ).flatten()

        # Get top_n similar (exclude itself)
        similar_indices = similarity_scores.argsort()[::-1]
        similar_indices = [i for i in similar_indices if i != idx][:top_n]

        similar_works = []
        for i in similar_indices:
            similar_works.append({
                "work_id":    self.work_ids[i],
                "similarity": round(float(similarity_scores[i]), 4),
            })

        return {
            "work_id":      work_id,
            "similar_works": similar_works,
        }

    # =====================================================
    # 3. DÉTECTION DES REVIEWERS BIAISÉS
    # =====================================================
    def detect_biased_reviewer(self, reviewer_id: int, threshold: float = 3.0) -> dict:
        """
        Détecte si un reviewer est biaisé :
        Compare la moyenne de ses notes à la moyenne globale.
        Si l'écart dépasse le threshold → biaisé.
        """
        reviewer_reviews = self.reviews[self.reviews["reviewer_id"] == reviewer_id]["note"]

        if reviewer_reviews.empty:
            return {"reviewer_id": reviewer_id, "is_biased": False, "message": "No reviews found"}

        global_mean   = float(self.reviews["note"].mean())
        reviewer_mean = float(reviewer_reviews.mean())
        deviation     = abs(reviewer_mean - global_mean)

        is_biased = deviation > threshold
        bias_type = None

        if is_biased:
            bias_type = "Trop sévère" if reviewer_mean < global_mean else "Trop généreux"

        return {
            "reviewer_id":   reviewer_id,
            "reviewer_mean": round(reviewer_mean, 2),
            "global_mean":   round(global_mean, 2),
            "deviation":     round(deviation, 2),
            "is_biased":     is_biased,
            "bias_type":     bias_type,
        }

    def detect_all_biased_reviewers(self, threshold: float = 3.0) -> pd.DataFrame:
        """Détecte tous les reviewers biaisés."""
        results = []
        for reviewer_id in self.reviews["reviewer_id"].unique():
            result = self.detect_biased_reviewer(reviewer_id, threshold)
            if result["is_biased"]:
                results.append(result)
        return pd.DataFrame(results) if results else pd.DataFrame()

    # =====================================================
    # 4. SAVE / LOAD (joblib)
    # =====================================================
    def save(self, path: str = "models/peer_review_model.joblib"):
        """Sauvegarde le modèle entraîné."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "vectorizer":   self.vectorizer,
            "scaler":       self.scaler,
            "tfidf_matrix": self.tfidf_matrix,
            "work_ids":     self.work_ids,
        }, path)
        print(f"✅ Model saved to {path}")

    @classmethod
    def load(cls, path: str, reviews_df: pd.DataFrame, works_df: pd.DataFrame):
        """Recharge un modèle sauvegardé sans ré-entraînement."""
        instance = cls.__new__(cls)
        instance.reviews = reviews_df.copy()
        instance.works   = works_df.copy()
        instance.reviews.columns = instance.reviews.columns.str.strip().str.lower()
        instance.works.columns   = instance.works.columns.str.strip().str.lower()

        data = joblib.load(path)
        instance.vectorizer   = data["vectorizer"]
        instance.scaler       = data["scaler"]
        instance.tfidf_matrix = data["tfidf_matrix"]
        instance.work_ids     = data["work_ids"]
        print(f"✅ Model loaded from {path}")
        return instance