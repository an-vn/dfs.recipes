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

print(settings.model_dump())
