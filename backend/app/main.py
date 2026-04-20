from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, chat
from app.db import init_db
from app.api import auth as auth_api

app = FastAPI(title="PDF QA Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(auth_api.router, prefix="/api")


@app.get("/health")
def health():
    return {"ok": True}

