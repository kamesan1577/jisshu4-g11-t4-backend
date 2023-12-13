import os
import time
import logging
import json
import hashlib
from .lib import chat_api, models, suggestion_api
from .lib.redis_client import RedisClient
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv


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
        "https://twitter.com",
        "http://localhost*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv(verbose=True)


# lambdaにデプロイすると動かない(そもそもいらない気がするけど)
@app.get("/")
def read_root():
    return {"Hello": "World"}


# ツイートの修正
@app.post("/moderations")
async def post_completion(
    request: models.ModerationsRequest,
) -> models.Moderations:
    # プロンプトをリストで渡した場合はスレッドとして扱う
    response = chat_api.chat_modelate(
        request.prompt, request.user_id, request.model, request.response_language
    )
    return models.Moderations(response=response)


# ツイートの修正が必要かどうかを判定(boolean)
@app.post("/moderations/suggestions/safety")
async def judge_safety(request: models.SuggestionsRequest) -> models.IsNotSafe:
    # try:
    start_time = time.time()
    hash_key = hashlib.sha256(
        (request.prompt + "is_required_moderation").encode()
    ).hexdigest()

    cached = RedisClient.get_value(hash_key)

    if cached:
        flag = json.loads(cached)["is_required_moderation"]
        logger.debug("cache hit")
    else:
        flag = suggestion_api.is_required_moderation(request.prompt)
        RedisClient.set_value(
            hash_key,
            json.dumps(jsonable_encoder(models.IsNotSafe(is_required_moderation=flag))),
            60 * 60 * 24 * 7,
        )

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
    return models.IsNotSafe(is_required_moderation=flag)
    # except Exception as e:
    #     logger.error(e)
    #     raise HTTPException(status_code=500, detail="Safety judgement failed")


# タイムラインの投稿に安全性のラベルを付与する(プロンプトを与えたgpt-3.5を使用したバージョン)
@app.post("/moderations/suggestions/timeline-safety")
async def judge_safety_timeline_completion(
    request: models.TimeLineRequest,
) -> models.TimeLineSafety:
    # try:
    start_time = time.time()
    safety_levels = await suggestion_api.async_get_safety_level(request.prompts)

    responses = [
        models.SafetyLevel(post=prompt, level=int(safety_level))
        for prompt, safety_level in zip(request.prompts, safety_levels)
    ]
    try:
        logger.debug(f"実行時間:{time.time() - start_time}秒")
        # print(f"実行時間:{time.time() - start_time}秒")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Log send failed")
    return models.TimeLineSafety(response=responses)
    # except Exception as e:
    #     logger.error(e)
    #     raise HTTPException(status_code=500, detail="Safety judgement failed")


# タイムラインの投稿に安全性のラベルを付与する(moderation APIを使用したバージョン)
@app.post("/moderations/suggestions/timeline-safety-with-moderation-api")
async def judge_safety_timeline_moderation(
    request: models.TimeLineRequest,
) -> models.TimeLineSafety:
    # TODO 非同期処理に対応させる
    try:
        start_time = time.time()
        response = []
        for post in request.prompts:
            hash_key = hashlib.sha256(
                (post + "safety_level_with_moderation_api").encode()
            ).hexdigest()
            cached = RedisClient.get_value(hash_key)

            if cached:
                safety_level = json.loads(cached)["level"]
                logger.debug("cache hit")
                response.append(models.SafetyLevel(post=post, level=safety_level))
            else:
                safety_level = int(suggestion_api.is_required_moderation(post))
                RedisClient.set_value(
                    hash_key,
                    json.dumps(
                        jsonable_encoder(
                            models.SafetyLevel(post=post, level=safety_level)
                        )
                    ),
                    expire_time=60 * 60 * 24 * 7,
                )
                response.append(models.SafetyLevel(post=post, level=safety_level))
            try:
                logger.debug(f"実行時間:{time.time() - start_time}秒")
            except Exception as e:
                logger.error(e)
                raise HTTPException(status_code=500, detail="Log send failed")
        return models.TimeLineSafety(response=response)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Safety judgement failed")


handler = Mangum(app, lifespan="off")
