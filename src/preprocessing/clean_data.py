import pandas as pd
import os

# =========================
# PATHS
# =========================
RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

# create processed folder if not exists
os.makedirs(PROCESSED_PATH, exist_ok=True)

print("🚀 Starting data cleaning process...")

# =========================
# 1. LOAD DATA
# =========================
try:
    students = pd.read_csv(f"{RAW_PATH}/students.csv")
    works = pd.read_csv(f"{RAW_PATH}/works.csv")
    reviews = pd.read_csv(f"{RAW_PATH}/reviews.csv")

    print("✅ Raw data loaded successfully")

except Exception as e:
    print("❌ Error loading raw data:", e)
    exit()


# =========================
# 2. CLEAN STUDENTS
# =========================
students = students.drop_duplicates()
students = students.dropna()

# normalize columns if needed
students.columns = [col.lower() for col in students.columns]


# =========================
# 3. CLEAN WORKS
# =========================
works = works.drop_duplicates()
works = works.dropna()
works.columns = [col.lower() for col in works.columns]


# =========================
# 4. CLEAN REVIEWS
# =========================
reviews = reviews.drop_duplicates()
reviews = reviews.dropna()
reviews.columns = [col.lower() for col in reviews.columns]

# convert score if exists
if "score" in reviews.columns:
    reviews["score"] = pd.to_numeric(reviews["score"], errors="coerce")


# =========================
# 5. SAVE PROCESSED DATA
# =========================
students.to_csv(f"{PROCESSED_PATH}/students_clean.csv", index=False)
works.to_csv(f"{PROCESSED_PATH}/works_clean.csv", index=False)
reviews.to_csv(f"{PROCESSED_PATH}/reviews_clean.csv", index=False)

print("🎯 Data successfully saved in processed/ folder")
print("📊 Students:", len(students))
print("📄 Works:", len(works))
print("⭐ Reviews:", len(reviews))
print("✅ Done!")