"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TI_", extra="ignore")

    base_url: str = "https://www.tokyoinsider.net"
    mirrors: list[str] = [
        "https://www.tokyoinsider.net",
        "https://www.tokyoinsider.com",
        "https://www.tokyoinsider.org",
    ]

    impersonate: str = "chrome124"
    proxy: str | None = None
    flaresolverr_url: str | None = None

    timeout: float = 30.0
    max_retries: int = 3
    retry_base: float = 0.6
    min_interval: float = 0.35

    cache_ttl: int = 300
    catalog_ttl: int = 21600
    search_ttl: int = 60

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )


settings = Settings()
