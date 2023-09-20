import os
from lib import chat_api
from fastapi import FastAPI
from mangum import Mangum
import openai
from dotenv import load_dotenv

app = FastAPI()
load_dotenv(verbose=True)
openai.api_key = os.environ.get("INIAD_OPENAI_API_KEY")
openai.api_base = "https://api.openai.iniad.org/api/v1"


@app.get("/")
def read_root():
    return {"Hello": "World"}


# /completion
@app.get("/completion/post")
async def post_completion(
    prompt: str, model: str = "gpt-3.5-turbo", response_language: str = "日本語"
):
    return chat_api.chat_modelate(prompt, model, response_language)


handler = Mangum(app, lifespan="off")
