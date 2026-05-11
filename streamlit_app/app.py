import streamlit as st
import requests
import pandas as pd

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
students = fetch("students")
works = fetch("works")
reviews = fetch("reviews?limit=1000")
student_rank = fetch("ranking/students")
work_rank = fetch("ranking/works")
stats = fetch("stats")

df_students = pd.DataFrame(students)
df_works = pd.DataFrame(works)
df_reviews = pd.DataFrame(reviews)

# =========================
# 📊 TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📊 Stats", "🏆 Rankings", "📂 Data"])

# =========================
# 📊 TAB 1 — STATS
# =========================
with tab1:
    st.header("📊 Global Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Students", stats.get("students", 0))
    col2.metric("Works", stats.get("works", 0))
    col3.metric("Reviews", stats.get("reviews", 0))

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
        st.dataframe(pd.DataFrame(work_rank), width="stretch")
    else:
        st.warning("No work ranking")

    st.header("👤 Student Ranking")

    if student_rank:
        st.dataframe(pd.DataFrame(student_rank), width="stretch")
    else:
        st.warning("No student ranking")

# =========================
# 📂 TAB 3 — DATA
# =========================
with tab3:
    st.header("👤 Students")

    if not df_students.empty:
        st.dataframe(df_students, width="stretch")
    else:
        st.warning("No students data")

    st.header("📄 Works")

    if not df_works.empty:
        st.dataframe(df_works, width="stretch")
    else:
        st.warning("No works data")

    st.header("⭐ Reviews")

    if not df_reviews.empty:
        st.dataframe(df_reviews, width="stretch")
    else:
        st.warning("No reviews data")