from redis.asyncio import Redis


redis_conn = Redis(decode_responses=True,host='localhost',port=6379)