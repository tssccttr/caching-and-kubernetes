import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from joblib import load
from redis import asyncio

logger = logging.getLogger(__name__)
model = None

LOCAL_REDIS_URL = "redis://localhost:6379/0"


@asynccontextmanager
async def lifespan_mechanism(app: FastAPI):
    logging.info("Starting up Lab3 API")

    # Load the Model on Startup
    global model
    model = load("model_pipeline.pkl")

    # Load the Redis Cache
    HOST_URL = ...  # replace this according to the Lab Requirements
    redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)

    # We initialize the connection to Redis and declare that all keys in the
    # database will be prefixed with w255-cache-predict. Do not change this
    # prefix for the submission.
    FastAPICache.init(RedisBackend(redis), prefix="w255-cache-prediction")

    yield
    # We don't need a shutdown event for our system, but we could put something
    # here after the yield to deal with things during shutdown
    logging.info("Shutting down Lab3 API")


sub_application_housing_predict = FastAPI(lifespan=lifespan_mechanism)


# Do not change this function name.
# See the Input Vectorization subsection in the readme for more instructions
async def multi_predict():
    pass
