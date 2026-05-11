from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import students, works, reviews, ranking, stats

app = FastAPI(title="Peer Review API")

# =========================
# 🌐 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES REGISTER
# =========================
app.include_router(students.router)
app.include_router(works.router)
app.include_router(reviews.router)
app.include_router(ranking.router)
app.include_router(stats.router)

# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"message": "API is running 🚀"}