import re
import asyncio
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from . import chat_api
from .redis_client import RedisClient


def is_required_moderation(prompt: str) -> bool:
    """文字列を受け取り、修正が必要かどうかを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        bool: 修正が必要ならTrue、必要でなければFalse
    """
    clean_text = _delete_html_tag(prompt)
    score = chat_api.safety_scoring(clean_text)
    if score.results[0].flagged:
        flag = True
    else:
        flag = False
    return flag


def get_safety_level(prompt: str) -> int:
    """
    文字列を受け取り、その安全性レベルを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        int: 安全性レベル（三段階、0が一番安全）
    """
    clean_text = _delete_html_tag(prompt)
    score = chat_api.get_safety_level(clean_text)
    return score


# TODO キャッシングと判定処理の責任を分離したい
async def async_get_safety_level(prompts: list[str])-> list[int]:
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
            tasks = [loop.run_in_executor(executor,chat_api.get_safety_level,prompt) for prompt in uncached_prompts]
            uncached_responses = await asyncio.gather(*tasks)

        for index, response in zip(uncached_indices,uncached_responses):
            hash_key = hash_key = hashlib.sha256((uncached_prompts[index] + "safety_level").encode()).hexdigest()
            RedisClient.set_value(hash_key,json.dumps({"post": uncached_prompts[index], "level": response}),expire_time=60 * 60 * 24 * 7)
            responses[index] = response

    return responses



def _delete_html_tag(text: str):
    # FIXME HTMLじゃなくても正規表現に引っかかる可能性がある
    clean_text = re.sub(r"<[^>]+>", " ", text)
    return clean_text
