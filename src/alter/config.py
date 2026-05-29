from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseModel):
    name: str = Field("Alter", description="Claude code project")
    version: str = Field("0.1.0", description="Version of the app")

class OpenAiConfig(BaseModel):
    api_key: SecretStr = Field(..., description="OpenAI API key")
    base_url: str = Field("https://api.openai.com/v1", description="Base URL for OpenAI API")
    model: str = Field("qwen2:1.5b")

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    app_config: AppConfig = AppConfig()
    open_ai_config: OpenAiConfig

config = Config()