import streamlit as st
import requests
import pandas as pd
import sys
import os

# Fix path to find src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.model import Model

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="Peer Review Dashboard",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

st.title("📊 Peer Review System")

# =========================
# ⚡ FAST FETCH (CACHE)
# =========================
@st.cache_data(ttl=60)
def fetch(endpoint):
    try:
        res = requests.get(f"{API_URL}/{endpoint}", timeout=5)
        return res.json()
    except Exception as e:
        st.error(f"API error on {endpoint}: {e}")
        return []

# =========================
# 📡 LOAD DATA
# =========================
students    = fetch("students")
works       = fetch("works")
reviews     = fetch("reviews?limit=1000")
student_rank = fetch("ranking/students")
work_rank   = fetch("ranking/works")
stats       = fetch("stats")

df_students = pd.DataFrame(students)
df_works    = pd.DataFrame(works)
df_reviews  = pd.DataFrame(reviews)

# =========================
# 🤖 LOAD AI MODEL
# =========================
@st.cache_resource
def load_model(reviews_df, works_df):
    return Model(reviews_df=reviews_df, works_df=works_df)

# =========================
# 📊 TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Stats",
    "🏆 Rankings",
    "📂 Data",
    "🤖 AI Model"
])

# =========================
# 📊 TAB 1 — STATS
# =========================
with tab1:
    st.header("📊 Global Statistics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Students", stats.get("students", 0))
    col2.metric("Works",    stats.get("works", 0))
    col3.metric("Reviews",  stats.get("reviews", 0))

    st.subheader("⭐ Notes Distribution")

    if not df_reviews.empty and "note" in df_reviews.columns:
        st.bar_chart(df_reviews["note"].value_counts())
    else:
        st.warning("No notes data available")

# =========================
# 🏆 TAB 2 — RANKINGS
# =========================
with tab2:
    st.header("🏆 Work Ranking")
    if work_rank:
        st.dataframe(pd.DataFrame(work_rank), use_container_width=True)
    else:
        st.warning("No work ranking")

    st.header("👤 Student Ranking")
    if student_rank:
        st.dataframe(pd.DataFrame(student_rank), use_container_width=True)
    else:
        st.warning("No student ranking")

# =========================
# 📂 TAB 3 — DATA
# =========================
with tab3:
    st.header("👤 Students")
    if not df_students.empty:
        st.dataframe(df_students, use_container_width=True)
    else:
        st.warning("No students data")

    st.header("📄 Works")
    if not df_works.empty:
        st.dataframe(df_works, use_container_width=True)
    else:
        st.warning("No works data")

    st.header("⭐ Reviews")
    if not df_reviews.empty:
        st.dataframe(df_reviews, use_container_width=True)
    else:
        st.warning("No reviews data")

# =========================
# 🤖 TAB 4 — AI MODEL
# =========================
with tab4:
    st.header("🤖 AI Model — Peer Review Analysis")

    if df_reviews.empty or df_works.empty:
        st.warning("⚠️ No data available for the AI model.")
    else:
        # Load model
        with st.spinner("🔄 Training AI model..."):
            model = load_model(df_reviews, df_works)

        st.success("✅ Model ready!")
        st.divider()

        # ── 1. Classification des travaux ──────────────────────────
        st.subheader("📊 1. Classification des travaux")

        with st.spinner("Classifying works..."):
            df_classified = model.classify_all_works()

        if not df_classified.empty:
            # Color by classification
            col1, col2, col3 = st.columns(3)
            col1.metric("🟢 Excellent", len(df_classified[df_classified["classification"] == "Excellent"]))
            col2.metric("🟡 Moyen",     len(df_classified[df_classified["classification"] == "Moyen"]))
            col3.metric("🔴 Faible",    len(df_classified[df_classified["classification"] == "Faible"]))

            st.dataframe(
                df_classified.style.applymap(
                    lambda v: "background-color: #d4edda" if v == "Excellent"
                    else ("background-color: #fff3cd" if v == "Moyen"
                    else ("background-color: #f8d7da" if v == "Faible" else "")),
                    subset=["classification"]
                ),
                use_container_width=True
            )

            # Bar chart of averages
            st.bar_chart(df_classified.set_index("work_id")["average"])

        st.divider()

        # ── 2. Similarité des travaux ───────────────────────────────
        st.subheader("🔍 2. Similarité des travaux (TF-IDF + Cosine Similarity)")

        available_works = model.work_ids if model.work_ids else []

        if available_works:
            selected_work = st.selectbox(
                "Choisir un work_id :",
                options=available_works
            )

            if st.button("🔍 Trouver les travaux similaires"):
                result = model.find_similar_works(selected_work, top_n=3)
                if result["similar_works"]:
                    st.dataframe(pd.DataFrame(result["similar_works"]), use_container_width=True)
                else:
                    st.info("Aucun travail similaire trouvé.")
        else:
            st.warning("Pas assez de données pour la similarité.")

        st.divider()

        # ── 3. Détection des reviewers biaisés ─────────────────────
        st.subheader("⚠️ 3. Détection des Reviewers Biaisés")

        threshold = st.slider(
            "Seuil de biais (écart par rapport à la moyenne) :",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5
        )

        if st.button("⚠️ Détecter les reviewers biaisés"):
            with st.spinner("Analyzing reviewers..."):
                df_biased = model.detect_all_biased_reviewers(threshold=threshold)

            if not df_biased.empty:
                st.warning(f"⚠️ {len(df_biased)} reviewer(s) biaisé(s) détecté(s) !")
                st.dataframe(df_biased, use_container_width=True)

                # Chart
                st.bar_chart(df_biased.set_index("reviewer_id")["deviation"])
            else:
                st.success("✅ Aucun reviewer biaisé détecté avec ce seuil.")

        st.divider()

        # ── 4. Save model ───────────────────────────────────────────
        st.subheader("💾 4. Sauvegarder le modèle")

        if st.button("💾 Sauvegarder le modèle (joblib)"):
            model.save("models/peer_review_model.joblib")
            st.success("✅ Modèle sauvegardé dans models/peer_review_model.joblib")