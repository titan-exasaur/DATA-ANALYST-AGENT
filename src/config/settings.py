from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # LLM
    openai_api_key: str = Field(default="")
    azure_openai_endpoint: str = Field(default="")
    azure_openai_api_key: str = Field(default="")
    azure_openai_deployment: str = Field(default="gpt-4o")

    # Azure Blob
    azure_storage_connection_string: str = Field(default="")
    azure_storage_container_name: str = Field(default="analyst-uploads")

    # MongoDB
    mongo_uri: str = Field(default="mongodb://localhost:27017")
    mongo_db_name: str = Field(default="ai_analyst")

    # App
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    max_upload_size_mb: int = Field(default=50)
    allowed_extensions: str = Field(default="csv,xlsx,xls")

    @property
    def allowed_ext_list(self) -> list[str]:
        return [e.strip() for e in self.allowed_extensions.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()