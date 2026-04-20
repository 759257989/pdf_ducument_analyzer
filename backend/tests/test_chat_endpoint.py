from unittest.mock import patch

from fastapi.testclient import TestClient

from app.auth import create_token, hash_password
from app.db import Document, SessionLocal, User, init_db
from app.main import app

init_db()
client = TestClient(app)


def _seed_user():
    db = SessionLocal()
    user = User(id="u-test", username="tester", password_hash=hash_password("password123"))
    db.merge(user)
    db.commit()
    db.close()


def _auth_headers():
    _seed_user()
    token = create_token("u-test")
    return {"Authorization": f"Bearer {token}"}


def _seed_doc():
    db = SessionLocal()
    doc = Document(id="seed", user_id="u-test", filename="seed.pdf", status="ready",
                   page_count=1, chunk_count=1)
    db.merge(doc)
    db.commit()
    db.close()


def test_empty_question_is_rejected():
    r = client.post("/api/chat", json={"question": "  ", "doc_ids": ["seed"]}, headers=_auth_headers())
    assert r.status_code == 400


def test_no_doc_selected_is_rejected():
    r = client.post("/api/chat", json={"question": "hi", "doc_ids": []}, headers=_auth_headers())
    assert r.status_code == 400


def test_no_hits_returns_honest_no_answer():
    """Critical invariant: when no hits are found, the LLM should not be allowed to generate an answer."""
    _seed_doc()
    with patch("app.api.chat.retrieve", return_value=[]):
        r = client.post("/api/chat", json={"question": "xxxxx", "doc_ids": ["seed"]}, headers=_auth_headers())
    assert r.status_code == 200
    body = r.json()
    answer_text = body["answer"].lower()
    assert "没有找到" in body["answer"] or "not find" in answer_text or "couldn't find" in answer_text
    assert body["citations"] == []