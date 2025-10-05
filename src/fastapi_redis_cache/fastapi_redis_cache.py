import pickle
import hashlib

from typing             import Callable
from functools          import wraps

from fastapi import Request, Response
from redis.exceptions   import ConnectionError as RedisConnectionError
from redis.asyncio      import Redis

def basic_key_builder(
    func: Callable,
    *args,
    **kwargs
):
    print(f"{kwargs=}")
    args_repr   = repr(args)
    kwargs_repr = repr(sorted(kwargs.items()))
    token       = FastAPIRedisCache.get_hash_function()(f"{FastAPIRedisCache.get_token_magic()}|{args_repr}|{kwargs_repr}".encode()).hexdigest()

    return f"{FastAPIRedisCache.get_prefix()}/{func.__module__}.{func.__name__}:{token}"

def fastapi_key_builder(
    func: Callable,
    *args,
    **kwargs,
) -> str:    
    filtered_kwargs = {
        k: v for k, v in kwargs.items() 
        if not k.startswith("__") and not isinstance(v, (Request, Response))      
    }
    return basic_key_builder(func, *args , **filtered_kwargs)

class FastAPIRedisCache:    
    _redis          = None
    _magic          = None
    _prefix         = None
    _expire         = None
    _serializer     = None
    _deserializer   = None
    _key_builder    = None
    _hash_function  = None

    @classmethod
    def init(
        cls, 
        redis           : Redis, 
        prefix          : str       = "",
        serializer      : Callable  = pickle.dumps, 
        deserializer    : Callable  = pickle.loads,
        hash_function   : Callable  = hashlib.sha256,
        token_magic     : str       = "FARCv1",
        key_builder     : Callable  = fastapi_key_builder,
        expire          : int       = 10
    ):
        cls._redis          = redis
        cls._prefix         = prefix
        cls._expire         = expire
        cls._token_magic    = token_magic
        cls._serializer     = serializer
        cls._deserializer   = deserializer
        cls._key_builder    = key_builder
        cls._hash_function  = hash_function

    @classmethod
    async def check_connection(cls) -> bool:
        if cls._redis is None:
            raise ConnectionError(f"Missing connection to Redis")
    
        try:
            if not await cls._redis.ping():
                raise ConnectionError("Redis connection failed to respond to PING")
        except RedisConnectionError as e:
            raise ConnectionError(f"Could not connect to Redis: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
    
        return True

    @classmethod
    def close_redis(cls) -> str:
        return cls._redis.close()

    @classmethod
    def get_redis(cls) -> str:
        return cls._redis
    
    @classmethod
    def get_prefix(cls) -> str:
        return cls._prefix

    @classmethod
    def get_expire(cls) -> str:
        return cls._expire

    @classmethod
    def get_token_magic(cls) -> str:
        return cls._token_magic

    @classmethod
    def get_serializer(cls) -> str:
        return cls._serializer

    @classmethod
    def get_deserializer(cls) -> str:
        return cls._deserializer

    @classmethod
    def get_key_builder(cls) -> str:
        return cls._key_builder

    @classmethod
    def get_hash_function(cls) -> str:
        return cls._hash_function

    @classmethod
    async def invalidate(cls, pattern: str = "*", use_prefix = True) -> None:
        redis = cls._redis
        mask  = cls._prefix + "/" + pattern if use_prefix else pattern

        pipe = redis.pipeline(transaction=False)
        async for key in redis.scan_iter(match=mask):            
            pipe.delete(key)

        await pipe.execute()

    @classmethod
    async def get_keys(cls, pattern: str = "*", use_prefix = True) -> list[str]:
        redis = cls._redis
        mask  = cls._prefix + "/" + pattern if use_prefix else pattern
        
        keys = []
        async for key in redis.scan_iter(match=mask):
           keys.append(key)
        return keys

def cache(expire = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):           
            redis   = FastAPIRedisCache.get_redis()
            key     = FastAPIRedisCache.get_key_builder()(func, *args, **kwargs)
            ex      = expire if expire is not None else FastAPIRedisCache.get_expire()

            if await redis.exists(key): 
                return FastAPIRedisCache.get_deserializer()(await redis.get(key))
            
            value = await func(*args, **kwargs)

            if ex:
                await redis.set(key, FastAPIRedisCache.get_serializer()(value), ex = ex)
            else:
                await redis.set(key, FastAPIRedisCache.get_serializer()(value))

            return value        
        return wrapper
    return decorator