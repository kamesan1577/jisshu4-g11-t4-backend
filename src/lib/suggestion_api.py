import asyncio
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from . import chat_api
from .redis_client import RedisClient
from .models import SafetyLevel
from fastapi.encoders import jsonable_encoder


def is_required_moderation(prompt: str, custom_client=None) -> bool:
    """文字列を受け取り、修正が必要かどうかを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        bool: 修正が必要ならTrue、必要でなければFalse
    """
    score = chat_api.safety_scoring(prompt, custom_client)
    if score.results[0].flagged:
        flag = True
    else:
        flag = False
    return flag


def get_safety_level(prompt: str, custom_client=None) -> int:
    """
    文字列を受け取り、その安全性レベルを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        int: 安全性レベル（三段階、0が一番安全）
    """

    score = chat_api.get_safety_level(prompt, custom_client)
    return score


# TODO キャッシングと判定処理の責任を分離したい
async def async_get_safety_level(prompts: list[str], custom_client=None) -> list[int]:
    """
    文字列のリストを受け取り、それらについての安全性レベルを非同期で判定する

    Args:
        prompts (list[str]): 判定対象の文字列のリスト
    Returns:
        list[int]: 安全性レベルのリスト（三段階、0が一番安全）
    """
    loop = asyncio.get_event_loop()
    responses = [None] * len(prompts)

    # キャッシュヒットしたプロンプトとしなかったプロンプトの順番がごちゃまぜにならないためのリスト
    uncached_prompts = []
    uncached_indices = []

    for i, prompt in enumerate(prompts):
        hash_key = hashlib.sha256((prompt + "safety_level").encode()).hexdigest()
        cached = RedisClient.get_value(hash_key)
        if cached:
            responses[i] = json.loads(cached)["level"]
        else:
            uncached_prompts.append(prompt)
            uncached_indices.append(i)

    # キャッシュされていないプロンプトを非同期で処理する
    if uncached_prompts:
        with ThreadPoolExecutor() as executor:
            tasks = [
                loop.run_in_executor(executor, get_safety_level, prompt, custom_client)
                for prompt in uncached_prompts
            ]
            uncached_responses = await asyncio.gather(*tasks)

        for index, response in zip(uncached_indices, uncached_responses):
            prompt = uncached_prompts[uncached_indices.index(index)]
            hash_key = hash_key = hashlib.sha256(
                (prompt + "safety_level").encode()
            ).hexdigest()
            RedisClient.set_value(
                hash_key,
                json.dumps(jsonable_encoder(SafetyLevel(post=prompt, level=response))),
                expire_time=60 * 60 * 24 * 7,
            )
            responses[index] = response

    return responses
