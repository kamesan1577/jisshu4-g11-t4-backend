import os
from typing import Union
from .lib import chat_api
from fastapi import FastAPI
from mangum import Mangum
import openai
from dotenv import load_dotenv
from pydantic import BaseModel


if os.environ.get("APP_ENV") == "DEV":
    app = FastAPI()
elif os.environ.get("APP_ENV") == "STAGE":
    app = FastAPI(openapi_prefix="/dev")
elif os.environ.get("APP_ENV") == "PROD":
    app = FastAPI(openapi_prefix="/prod")
else:
    app = FastAPI()

load_dotenv(verbose=True)
openai.api_key = os.environ.get("INIAD_OPENAI_API_KEY")
openai.api_base = "https://api.openai.iniad.org/api/v1"


# リクエストのモデル
class Tweet(BaseModel):
    prompt: Union[str, list]
    user_id: str
    model: str = "gpt-3.5-turbo"
    response_language: str = "日本語"


# lambdaにデプロイすると動かない(そもそもいらない気がするけど)
@app.get("/")
def read_root():
    return {"Hello": "World"}


# ツイートの修正
@app.post("/moderations")
async def post_completion(
    tweet: Tweet,
):
    # プロンプトをリストで渡した場合はスレッドとして扱う
    return chat_api.chat_modelate(
        tweet.prompt, tweet.user_id, tweet.model, tweet.response_language
    )


handler = Mangum(app, lifespan="off")
