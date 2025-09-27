import dramatiq
from dramatiq.brokers.redis import RedisBroker
from backend.src.core.settings import get_settings

# Configure the Redis broker
redis_broker = RedisBroker(
    host=get_settings().REDIS_HOST, port=get_settings().REDIS_PORT
)
dramatiq.set_broker(redis_broker)
