import os
from .lib import chat_api
from fastapi import FastAPI
from mangum import Mangum
import openai
from dotenv import load_dotenv

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


@app.get("/")
def read_root():
    return {"Hello": "World"}


# /moderations
@app.get("/moderations")
async def post_completion(
    prompt: str,
    user_id: str,
    model: str = "gpt-3.5-turbo",
    response_language: str = "日本語",
):
    return chat_api.chat_modelate(prompt, user_id, model, response_language)


handler = Mangum(app, lifespan="off")
