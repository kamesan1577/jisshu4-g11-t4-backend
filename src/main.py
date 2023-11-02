import os
import logging
import hashlib
import json
from .lib import chat_api, models, suggestion_api
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum
import openai
from dotenv import load_dotenv
import redis

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

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


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


# ツイートの修正が必要かどうかを判定(list[str])
@app.post("/moderations/suggestions")
async def post_suggestions(request: models.SuggestionsRequest):
    try:
        hash_key = hashlib.sha256((request.prompt + "suggestions").encode()).hexdigest()
        cached = redis_client.get(hash_key)

        if cached:
            hidden_words = json.loads(cached.decode("utf-8"))["suggestions"]
            print("cache hit")
        else:
            # 修正対象の単語のリストを返す
            hidden_words = suggestion_api.get_hidden_words(request.prompt)
            redis_client.set(hash_key, json.dumps({"suggestions": hidden_words}))

        # 実行と同時にログに流す
        log = models.SuggestionsLog(
            user_id=request.user_id,
            post_id="hoge",
            original_text=request.prompt,
            hidden_texts=hidden_words,
        ).model_dump()
        try:
            logging.info(json.dumps(log))
        except Exception as e:
            logging.error(e)
            raise HTTPException(status_code=500, detail="Log send failed")
        return {"suggestions": hidden_words}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Suggestion failed")


# ツイートの修正が必要かどうかを判定(boolean)
@app.post("/moderations/suggestions/safety")
async def judge_safety(request: models.SuggestionsRequest):
    try:
        flag = suggestion_api.is_required_moderation(request.prompt)

        # 実行と同時にログに流す
        log = models.SafetyJudgementLog(
            user_id=request.user_id,
            post_id="hoge",
            prompt=request.prompt,
        ).model_dump()
        try:
            logging.info(json.dumps(log))
        except Exception as e:
            logging.error(e)
            raise HTTPException(status_code=500, detail="Log send failed")
        return {"is_required_moderation": flag}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Safety judgement failed")


# TLの検閲
@app.post("/redaction")
async def post_redaction(
    request: models.TimeLineRequest,
):
    try:
        response = []
        for post in request.prompts:
            # TODO コードが書き換わったときにキャッシュを消す
            hash_key = hashlib.sha256((post + "redaction").encode()).hexdigest()

            cached = redis_client.get(hash_key)

            if cached:
                hidden_text = json.loads(cached.decode("utf-8"))["hidden"]
                print("cache hit")
                response.append({"original": post, "hidden": hidden_text})
            else:
                hidden_text = suggestion_api.get_hidden_words(post)
                redis_client.set(hash_key, json.dumps({"hidden": hidden_text}))
                response.append({"original": post, "hidden": hidden_text})

        return {"response": response}

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Redaction failed")


# ツイートの修正を受け入れたかどうかをログに送信
@app.post("/poc/suggest-acceptance-collection")
async def post_is_accepted_suggestion(
    request: models.IsAcceptedSuggestionRequest,
):
    log = models.IsAcceptedSuggestionLog(
        user_id=request.user_id,
        post_id="hoge",
        is_accepted=request.is_accepted,
        is_edited_by_user=request.is_edited_by_user,
        original_text=request.original_text,
        hidden_texts=request.hidden_texts,
    ).model_dump()
    try:
        logging.info(json.dumps(log))
        return {"message": "success", "is_accepted": request.is_accepted}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Log send failed")


# 隠された文字列の統計情報をログに送信
# @app.post("/poc/hidden-text-collection")
# async def post_hidden_text_collection(
#     hidden_chars: models.HiddenChars,
# ):
#     log = models.SuggestionsLog(
#         user_id=hidden_chars.user_id,
#         post_id="hoge",
#         original_text=hidden_chars.original_text,
#         hidden_texts=hidden_chars.hidden_texts,
#     ).model_dump()
#     try:
#         logging.info(json.dumps(log))
#         return {"message": "success"}
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail="Log send failed")


handler = Mangum(app, lifespan="off")
