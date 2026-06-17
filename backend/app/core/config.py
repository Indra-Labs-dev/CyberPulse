from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CyberPulse"
    environment: str = "development"
    debug: bool = True

    database_url: str = "mysql+aiomysql://cyberpulse:cyberpulse@localhost:3306/cyberpulse"
    database_url_sync: str = "mysql+pymysql://cyberpulse:cyberpulse@localhost:3306/cyberpulse"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-to-a-long-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    scraping_enabled: bool = True
    scraping_interval_minutes: int = 15
    scraping_user_agent: str = "CyberPulseBot/1.0 (+https://indralabs.example)"

    cve_sync_enabled: bool = True
    cve_sync_interval_minutes: int = 60

    reports_dir: str = "./storage/reports"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
