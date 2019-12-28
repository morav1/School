import redis

from grading.configuration import REDIS_HOST, REDIS_PORT


def redis_client():
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def set_lock(key):
    client = redis_client()
    client.setnx(key, 'lock')
    client.expire(name=key, time=10)


def release_lock(key):
    client = redis_client()
    client.delete(key)