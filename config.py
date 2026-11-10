from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):

    database_url: str
    alembic_url: str


    access_token_expires_minutes: int
    refresh_token_expires_days: int
    jwt_algorithm: str
    jwt_secret_key: str


    email_host: str
    email_user: str
    email_password: str


    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


settings = Settings()