from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    data_dir: Path = Path("./data")

    # 文档分块参数
    chunk_size: int = 600
    chunk_overlap: int = 100

    # 检索返回参数
    retrieval_top_k: int = 6

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def sqlite_path(self) -> Path:
        return self.data_dir / "app.db"


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_dir.mkdir(parents=True, exist_ok=True)