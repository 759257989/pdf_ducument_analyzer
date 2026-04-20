from unittest.mock import patch

from app.services.retriever import retrieve


def test_retrieve_passes_doc_ids_to_vector_store():
    """Critical invariant: the selected doc_ids must be passed to the vector store, otherwise it will answer across documents."""
    with patch("app.services.retriever.embed_texts", return_value=[[0.1] * 1536]), \
         patch("app.services.retriever.chroma_query", return_value=[]) as mock_q:
        retrieve("test question", "u-test", ["doc-A", "doc-B"])
        _, kwargs = mock_q.call_args
        assert kwargs["user_id"] == "u-test"
        assert kwargs["doc_ids"] == ["doc-A", "doc-B"]