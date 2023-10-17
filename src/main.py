import os
import logging
import json
from .lib import chat_api, models, suggestion_api
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum
import openai
from dotenv import load_dotenv

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if os.environ.get("APP_ENV") == "DEV":
    app = FastAPI()
elif os.environ.get("APP_ENV") == "STAGE":
    app = FastAPI(openapi_prefix="/dev")
elif os.environ.get("APP_ENV") == "PROD":
    app = FastAPI(openapi_prefix="/prod")
else:
    app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://omochifestival.com",
        "https://misskey.io",
        "http://localhost*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv(verbose=True)
openai.api_key = os.environ.get("INIAD_OPENAI_API_KEY")
openai.api_base = "https://api.openai.iniad.org/api/v1"


# lambdaにデプロイすると動かない(そもそもいらない気がするけど)
@app.get("/")
def read_root():
    return {"Hello": "World"}


# ツイートの修正
@app.post("/moderations")
async def post_completion(
    request: models.ModerationsRequest,
):
    # プロンプトをリストで渡した場合はスレッドとして扱う
    response = chat_api.chat_modelate(
        request.prompt, request.user_id, request.model, request.response_language
    )
    return {"response": response}


# ツイートの修正を提案
@app.post("/moderations/suggestions")
async def post_suggestions(request: models.SuggestionsRequest):
    try:
        # 修正対象の単語のリストを返す
        hidden_words = suggestion_api.get_hidden_words(request.prompt)

        # 実行と同時にログに流す
        post_hidden_text_collection(
            models.HiddenChars(
                user_id=request.user_id,
                original_text=request.prompt,
                hidden_texts=hidden_words,
            )
        )
        return {"suggestions": hidden_words}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Suggestion failed")


# ツイートの修正を受け入れたかどうかをログに送信
@app.post("/poc/suggest-acceptance-collection")
async def post_is_accepted_suggestion(
    request: models.IsAcceptedSuggestionRequest,
):
    log = models.IsAcceptedSuggestionLog(
        user_id=request.user_id,
        post_id="hoge",
        is_accepted=request.is_accepted,
        original_text=request.original_text,
        hidden_texts=request.hidden_texts,
    ).model_dump()
    try:
        logging.info(log.json())
        return {"message": "success", "is_accepted": request.is_accepted}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Log send failed")


# 隠された文字列の統計情報をログに送信
@app.post("/poc/hidden-text-collection")
async def post_hidden_text_collection(
    hidden_chars: models.HiddenChars,
):
    log = models.SuggestionsLog(
        user_id=hidden_chars.user_id,
        post_id="hoge",
        original_text=hidden_chars.original_text,
        hidden_texts=hidden_chars.hidden_texts,
    ).model_dump()
    try:
        logging.info(json.dumps(log))
        return {"message": "success"}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Log send failed")


handler = Mangum(app, lifespan="off")
