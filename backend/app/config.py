from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "development"

    # Postgres
    postgres_user: str = "prevoto"
    postgres_password: str = "changeme"
    postgres_db: str = "prevoto"
    database_url: str = "postgresql+asyncpg://prevoto:changeme@postgres:5432/prevoto"

    # Redis
    redis_url: str = "redis://redis:6379/0"
    redis_ratelimit_url: str = "redis://redis:6379/1"

    # Admin
    admin_api_key: str = "changeme"

    # Beehiiv
    beehiiv_api_key: str = ""
    beehiiv_publication_id: str = ""

    # Cloudflare R2
    cloudflare_r2_access_key: str = ""
    cloudflare_r2_secret_key: str = ""
    cloudflare_r2_endpoint: str = ""
    cloudflare_r2_bucket: str = "prevoto-backups"

    # Wikimedia
    wikimedia_user_agent: str = "pre.voto-bot/1.0 (https://pre.voto; contact@pre.voto)"

    # Sentry
    sentry_dsn: str = ""

    # Public URLs
    public_api_url: str = "http://localhost"
    public_site_url: str = "http://localhost"

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_subscribe_per_hour: int = 5

    # Article preview
    admin_preview_token: str = ""

    # Veda
    veda_enabled_co: bool = False
    veda_start_co: str = ""
    veda_end_co: str = ""

    # SMTP (Mailpit in dev)
    smtp_host: str = "mailpit"
    smtp_port: int = 1025

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
