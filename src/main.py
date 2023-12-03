import os
import time
import logging
import hashlib
import json
from .lib import chat_api, models, suggestion_api
# from .lib.db_client import db_instance
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv
import redis

logger = logging.getLogger("PocLog")
logger.setLevel(logging.INFO)

if os.environ.get("APP_ENV") == "DEV":
    logger.setLevel(logging.DEBUG)
    app = FastAPI()
elif os.environ.get("APP_ENV") == "STAGE":
    app = FastAPI(openapi_prefix="/dev")
elif os.environ.get("APP_ENV") == "PROD":
    logger.setLevel(logging.ERROR)
    app = FastAPI(openapi_prefix="/master")
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
# @app.post("/moderations/suggestions")
# async def post_suggestions(request: models.SuggestionsRequest):
#     try:
#         start_time = time.time()
#         hash_key = hashlib.sha256((request.prompt + "suggestions").encode()).hexdigest()
#         cached = redis_client.get(hash_key)

#         if cached:
#             hidden_words = json.loads(cached.decode("utf-8"))["suggestions"]
#             # print("cache hit")
#         else:
#             # 修正対象の単語のリストを返す
#             hidden_words = suggestion_api.get_hidden_words(request.prompt)
#             redis_client.set(hash_key, json.dumps({"suggestions": hidden_words}))

#         # 実行と同時にログに流す
#         log = models.SuggestionsLog(
#             user_id=request.user_id,
#             post_id="hoge",
#             original_text=request.prompt,
#             hidden_texts=hidden_words,
#         ).model_dump()
#         try:
#             logger.info(json.dumps(log))
#             logger.debug(f"実行時間:{time.time() - start_time}秒")
#         except Exception as e:
#             logger.error(e)
#             raise HTTPException(status_code=500, detail="Log send failed")
#         return {"suggestions": hidden_words}
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Suggestion failed")


# ツイートの修正が必要かどうかを判定(boolean)
@app.post("/moderations/suggestions/safety")
async def judge_safety(request: models.SuggestionsRequest):
    try:
        start_time = time.time()
        hash_key = hashlib.sha256(
            (request.prompt + "is_required_moderation").encode()
        ).hexdigest()
        cached = redis_client.get(hash_key)

        if cached:
            flag = json.loads(cached.decode("utf-8"))["is_required_moderation"]
            logger.debug("cache hit")
        else:
            flag = suggestion_api.is_required_moderation(request.prompt)
            redis_client.set(hash_key, json.dumps({"is_required_moderation": flag}))
            redis_client.expire(hash_key, 60 * 60 * 24 * 7)

        # 実行と同時にログに流す
        log = models.SafetyJudgementLog(
            user_id=request.user_id,
            post_id="hoge",
            prompt=request.prompt,
        ).model_dump()
        try:
            logger.info(json.dumps(log))
            logger.debug(f"実行時間:{time.time() - start_time}秒")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail="Log send failed")
        return {"is_required_moderation": flag}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Safety judgement failed")

# タイムラインの投稿に安全性のラベルを付与する(プロンプトを与えたgpt-3.5を使用したバージョン)
@app.post("/moderations/suggestions/timeline-safety")
async def judge_safety(request: models.TimeLineRequest,):
    try:
        start_time = time.time()
        response = []
        for post in request.prompts:  
            hash_key = hashlib.sha256(
            (post + "safety_level").encode()
            ).hexdigest()
            cached = redis_client.get(hash_key)

            if cached:
                safety_level = json.loads(cached.decode("utf-8"))["level"]
                logger.debug("cache hit")
                response.append({"post": post,"level": safety_level})
            else:
                safety_level = suggestion_api.get_safety_level(post)
                redis_client.set(hash_key, json.dumps({"post":post,"level":safety_level}))
                redis_client.expire(hash_key, 60 * 60 * 24 * 7)
                response.append({"post": post,"level": safety_level})

            try:
                logger.debug(f"実行時間:{time.time() - start_time}秒")
            except Exception as e:
                logger.error(e)
                raise HTTPException(status_code=500, detail="Log send failed")
        return {"response":response}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Safety judgement failed")

# タイムラインの投稿に安全性のラベルを付与する(moderation APIを使用したバージョン)
@app.post("/moderations/suggestions/timeline-safety-with-moderation-api")
async def judge_safety(request: models.TimeLineRequest,):
    try:
        start_time = time.time()
        response = []
        for post in request.prompts:  
            hash_key = hashlib.sha256(
            (post + "safety_level_with_moderation_api").encode()
            ).hexdigest()
            cached = redis_client.get(hash_key)

            if cached:
                safety_level = json.loads(cached.decode("utf-8"))["level"]
                logger.debug("cache hit")
                response.append({"post": post,"level": safety_level})
            else:
                safety_level = int(suggestion_api.is_required_moderation(post))
                redis_client.set(hash_key, json.dumps({"post":post,"level":safety_level}))
                redis_client.expire(hash_key, 60 * 60 * 24 * 7)
                response.append({"post": post,"level": safety_level})

            try:
                logger.debug(f"実行時間:{time.time() - start_time}秒")
            except Exception as e:
                logger.error(e)
                raise HTTPException(status_code=500, detail="Log send failed")
        return {"response":response}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Safety judgement failed")

# # TLの検閲
# @app.post("/redaction")
# async def post_redaction(
#     request: models.TimeLineRequest,
# ):
#     try:
#         start_time = time.time()
#         response = []
#         for post in request.prompts:
#             # TODO コードが書き換わったときにキャッシュを消す
#             hash_key = hashlib.sha256((post + "redaction").encode()).hexdigest()

#             cached = redis_client.get(hash_key)

#             if cached:
#                 hidden_text = json.loads(cached.decode("utf-8"))["hidden"]
#                 # print("cache hit")
#                 response.append({"original": post, "hidden": hidden_text})
#             else:
#                 hidden_text = suggestion_api.get_hidden_words(post)
#                 redis_client.set(hash_key, json.dumps({"hidden": hidden_text}))
#                 response.append({"original": post, "hidden": hidden_text})
#         logger.debug(f"実行時間:{time.time() - start_time}秒")
#         return {"response": response}

#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Redaction failed")


# # ツイートの修正を受け入れたかどうかをログに送信
# @app.post("/poc/suggest-acceptance-collection")
# async def post_is_accepted_suggestion(
#     request: models.IsAcceptedSuggestionRequest,
# ):
#     log = models.IsAcceptedSuggestionLog(
#         user_id=request.user_id,
#         post_id="hoge",
#         is_accepted=request.is_accepted,
#         is_edited_by_user=request.is_edited_by_user,
#         original_text=request.original_text,
#         hidden_texts=request.hidden_texts,
#     ).model_dump()
#     try:
#         logger.info(json.dumps(log))
#         return {"message": "success", "is_accepted": request.is_accepted}
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Log send failed")


# @app.get("/moral-foundation/{sheet_name}/data")
# async def get_moral_foundation_data(sheet_name: str):
#     try:
#         data = db_instance.fetch_sheet_value(sheet_name)
#         return {"data": data}
#     except db_instance.SheetNotFoundError:
#         raise HTTPException(status_code=404, detail="Sheet not found")
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Data fetch failed")


# @app.post("/moral-foundation/{sheet_name}/data")
# async def post_moral_foundation_data(sheet_name: str, data: models.Sheet):
#     try:
#         db_instance.add_sheet_value(sheet_name, data)
#         return {"message": "success"}
#     except db_instance.SheetNotFoundError:
#         raise HTTPException(status_code=404, detail="Sheet not found")
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Data post failed")


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
#         logger.info(json.dumps(log))
#         return {"message": "success"}
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Log send failed")


handler = Mangum(app, lifespan="off")
