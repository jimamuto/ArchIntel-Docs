import os
import redis
import asyncio
from arq import create_pool
from arq.connections import RedisSettings

async def verify_redis():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    print(f"Testing connection to Redis at: {redis_url}")
    
    # Test standard redis connection
    try:
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Standard Redis ping successful")
    except Exception as e:
        print(f"❌ Standard Redis ping failed: {e}")
        return

    # Test arq connection
    try:
        pool = await create_pool(RedisSettings.from_dsn(redis_url))
        await pool.close()
        print("✅ Arq pool creation successful")
    except Exception as e:
        print(f"❌ Arq pool creation failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_redis())
