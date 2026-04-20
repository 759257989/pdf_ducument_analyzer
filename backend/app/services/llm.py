from openai import OpenAI
from app.config import settings

_client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a rigorous document question-answering assistant. Please strictly follow the rules below:

1: Answer questions only based on the provided [Document Excerpts] below.
2: If there is not enough information in the [Document Excerpts] to answer the question, respond exactly with:
"Sorry, I could not find relevant information in the uploaded document."
Do not fabricate information and do not rely on prior knowledge.
3: Every factual statement in your answer must include a citation in the format [Source: Page X] at the end of the sentence. If multiple sources apply, list multiple citations together.
5: Respond in the same language as the user's question (Chinese questions in Chinese, English questions in English).
6: Keep answers concise, direct, and well-structured."""


def _build_context(hits: list[dict]) -> str:
    blocks = []
    for h in hits:
        blocks.append(f"【fragment | source: page {h['page_number']}】\n{h['text']}")
    return "\n\n---\n\n".join(blocks)


def answer(question: str, hits: list[dict], history: list[dict]) -> str:
    context = _build_context(hits)
    user_msg = f"【document fragments】\n{context}\n\n【user question】\n{question}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # keep the recent history to avoid the too much token
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_msg})

    resp = _client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=messages,
        temperature=0.1,
    )
    return resp.choices[0].message.content