from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ticketing API"
    environment: str = "dev"
    debug: bool = True

    # 👉 TEMPORAIRE DEV (sans Docker)
    database_url: str = "sqlite:///./dev.db"

    # 👉 FUTUR (PostgreSQL)
    postgres_user: str = "ticketing"
    postgres_password: str = "ticketing"
    postgres_db: str = "ticketing"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    @property
    def postgres_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()