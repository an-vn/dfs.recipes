from pydantic import (
    BaseModel,
    Field
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    provider: str = Field(default='')
    api_key: str = Field(default='')
    api_type: str = Field(default='')
    api_version: str = Field(default='')


class Settings(BaseSettings):
    app_name: str = 'DFS Recipes'
    domains: set[str] = set()
    gemini_api_key: str = Field(default='')
    gemini_model: str = Field(default='gemini-2.0-flash-001')
    session_encryption_key: str = Field(default='')
    session_cookie_key: str = Field(default='DFS_SESSION')
    user_input_character_limit: int = Field(default=200)

    model_config = SettingsConfigDict(
        env_file=('.env', '.env.prod'),
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='_',
        env_nested_max_split=1,
        env_prefix='GENERATION_',
        # secrets_dir=('/var/run', '/run/secrets')
    )
    llm: LLMConfig = LLMConfig()


settings = Settings()
