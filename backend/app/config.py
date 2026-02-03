import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    app_host: str
    app_port: int
    database_url: str
    upload_dir: str
    max_upload_mb: int
    llm_provider: str
    openai_api_key: str
    openai_model: str
    anthropic_api_key: str
    anthropic_model: str
    case_study_xlsx_path: str | None

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            app_host=os.getenv("APP_HOST", "0.0.0.0"),
            app_port=int(os.getenv("APP_PORT", "8000")),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./data/app.db"),
            upload_dir=os.getenv("UPLOAD_DIR", "./data/uploads"),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "20")),
            llm_provider=os.getenv("LLM_PROVIDER", "anthropic"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            anthropic_model=os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-5-sonnet-20240620"),
            case_study_xlsx_path=os.getenv("CASE_STUDY_XLSX_PATH") or None,
        )
