from pydantic import BaseModel, Field
from openai import OpenAI
from alter.config import config

class OpenAIService:
    def __init__(self):
        self.base_url = config.open_ai_config.base_url
        self.api_key = config.open_ai_config.api_key
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        
    def create_chat_completion(self, model: str, messages: list[dict], **kwargs) -> dict:
        """Create a chat completion using the OpenAI API."""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.dict()