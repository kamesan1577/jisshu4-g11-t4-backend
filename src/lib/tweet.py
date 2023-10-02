from typing import Union
from pydantic import BaseModel


# リクエストのモデル
class Tweet(BaseModel):
    prompt: Union[str, list]
    user_id: str
    model: str = "gpt-3.5-turbo"
    response_language: str = "日本語"
