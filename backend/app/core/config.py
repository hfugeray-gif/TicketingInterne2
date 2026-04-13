from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Ticketing API"
    env: str = "dev"
    debug: bool = True

    # Base de données
    database_url: str = "sqlite:///./app.db"

    # Front / liens applicatifs
    app_base_url: str = "http://localhost:8501"

    # Emails
    emails_enabled: bool = False
    smtp_from: str = "no-reply@beam.local"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_use_tls: bool = False
    smtp_username: str = ""
    smtp_password: str = ""

    # CORS
    cors_allow_origins: str = "http://localhost:8501,http://127.0.0.1:8501"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()