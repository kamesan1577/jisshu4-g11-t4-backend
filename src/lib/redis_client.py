import os
import hashlib
import json
from dotenv import load_dotenv
import redis


class RedisClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls)
            load_dotenv(verbose=True)
            if "REDIS_PASSWORD" in os.environ:
                cls._instance.redis_client = redis.Redis(
                    host=os.environ["REDIS_HOST"],
                    port=os.environ.get("REDIS_PORT", 6379),
                    password=os.environ["REDIS_PASSWORD"],
                    db=0,
                    ssl=True,
                )
            else:
                cls._instance.redis_client = redis.Redis(
                    host=os.environ["REDIS_HOST"],
                    port=os.environ.get("REDIS_PORT", 6379),
                    db=0,
                )
        return cls._instance.redis_client

    @staticmethod
    def get_value(hash_key: str):
        redis_client = RedisClient()
        cached_value = redis_client.get(hash_key)
        if cached_value:
            try:
                return json.loads(cached_value.decode("utf-8"))
            except json.JSONDecodeError:
                # JSON 形式でない場合はそのまま返す
                return cached_value.decode("utf-8")
        return None

    @staticmethod
    def set_value(hash_key: str, value, expire_time=None):
        redis_client = RedisClient()
        redis_client.set(hash_key, json.dumps(value))
        if expire_time:
            redis_client.expire(hash_key, expire_time)
