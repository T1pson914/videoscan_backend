from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):

    database_url: str = ''
    alembic_url: str = ''


    access_token_expire_minutes: int = 0
    refresh_token_expire_days: int = 0
    jwt_alg: str = ''
    jwt_secret_key: str = ''


    email_host: str = ''
    email_user: str = ''
    email_password: str = ''


    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


settings = Settings()