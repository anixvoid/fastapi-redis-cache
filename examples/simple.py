import time
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi_redis_cache import FastAPIRedisCache, cache

from redis.asyncio  import Redis

async def lifespan(app: FastAPI):
    FastAPIRedisCache.init(
        redis = await Redis(
            host = "127.0.0.1",
            port = 6379
        ),
        prefix = "/cache"
    )
    if await FastAPIRedisCache.check_connection():
        print("Successful connection to Redis")
    yield
    await FastAPIRedisCache.close_redis()

app = FastAPI(lifespan=lifespan)

@app.get("/example/users")
@cache(expire=60)
async def get_users(request: Request, response: Response):
    time.sleep(2)
    
    return {
        "users": [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ],
        "timestamp": datetime.now()
    }

@app.get("/example/users/{user_id}")
@cache(expire=60)
async def get_user(user_id: int):
    time.sleep(2)

    print(f"Выполняется запрос для пользователя {user_id}")
    
    return {
        "user_id"   : user_id,
        "name"      : f"User {user_id}",
        "timestamp" : datetime.now()
    }

@app.get("/example/products")
@cache(expire=60)
async def get_products(
    category    : str = None,
    page        : int = 1,
    limit       : int = 10
):
    time.sleep(2)

    print(f"Запрос продуктов: category={category}, page={page}")
    
    return {
        "products": [
            {"id": 1, "name": f"Product in {category}", "page": page},
            {"id": 2, "name": f"Another product in {category}", "page": page}
        ],
        "filters": {
            "category": category,
            "page": page,
            "limit": limit
        },
        "timestamp" : datetime.now()
    }

@app.get("/cache/keys")
async def get_keys(
    pattern     = "*",
    use_prefix  = True
):
    return await FastAPIRedisCache.get_keys(pattern=pattern, use_prefix=use_prefix)

@app.post("/cache/invalidate")
async def get_keys(
    pattern     = "*",
    use_prefix  = True
):
    return await FastAPIRedisCache.invalidate(pattern=pattern, use_prefix=use_prefix)

if __name__ == "__main__":
    uvicorn.run(
        app     = "simple:app",
        host    = "0.0.0.0",
        port    = 8088,
        reload  = True
    )