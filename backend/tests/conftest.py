import os
import tempfile
import pytest


@pytest.fixture(scope="session", autouse=True)
def _test_env():
    tmp = tempfile.mkdtemp(prefix="pdfqa_test_")
    os.environ["DATA_DIR"] = tmp
    os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake")
    yield