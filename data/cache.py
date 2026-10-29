from redis.asyncio import Redis


# localhost пока что на время
redis_conn = Redis(decode_responses=True,host='localhost',port=6379)