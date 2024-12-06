import logging
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from joblib import load
from redis import asyncio
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List
import numpy as np

logger = logging.getLogger(__name__)
model = None

LOCAL_REDIS_URL = "redis://localhost:6379"


@asynccontextmanager
async def lifespan_mechanism(app: FastAPI):
    logging.info("Starting up Lab3 API")

    # Load the Model on Startup
    global model
    model = load("model_pipeline.pkl")

    # Load the Redis Cache
    HOST_URL = os.getenv("REDIS_URL", LOCAL_REDIS_URL)
    redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)

    # We initialize the connection to Redis and declare that all keys in the
    # database will be prefixed with w255-cache-predict. Do not change this
    # prefix for the submission.
    FastAPICache.init(RedisBackend(redis), prefix="w255-cache-prediction")

    yield
    logging.info("Shutting down Lab3 API")

class House(BaseModel):
    """Data model to parse the request body JSON for a single house."""
    model_config = ConfigDict(extra="forbid")

    MedInc: float = Field(ge=0)
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    @field_validator("Latitude")
    @classmethod
    def valid_latitude(cls, v: float) -> float:
        if -90 < v < 90:
            return v
        raise ValueError("Invalid value for Latitude")

    @field_validator("Longitude")
    @classmethod
    def valid_longitude(cls, v: float) -> float:
        if -180 < v < 180:
            return v
        raise ValueError("Invalid value for Longitude")

    def to_np(self) -> np.ndarray:
        return np.array([
            self.MedInc, self.HouseAge, self.AveRooms,
            self.AveBedrms, self.Population, self.AveOccup,
            self.Latitude, self.Longitude
        ]).reshape(1,8)

class BulkHousePredictionRequest(BaseModel):
    # data model for prediction requests
    model_config = ConfigDict(extra="forbid")
    houses: List[House]

    def to_np(self):
        return np.array([list(vars(house).values()) for house in self.houses])

class HousePrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prediction: float

class BulkHousePrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    predictions: List[float]

sub_application_housing_predict = FastAPI(lifespan=lifespan_mechanism)

# Do not change this function name.
# See the Input Vectorization subsection in the readme for more instructions
async def multi_predict(houses_data: List[House]) -> List[float]:
    # vectorized predictions on multiple house inputs, returns ist of predicted house prices
    if not houses_data:
        return []
    
    # converting to array for vectorized prediction
    request = BulkHousePredictionRequest(houses=houses_data)
    input_matrix = request.to_np()

    return model.predict(input_matrix).tolist()

@sub_application_housing_predict.post("/predict", response_model=HousePrediction)
@cache(expire=3600)
async def predict(house: House) -> HousePrediction:
    predictions = await multi_predict([house])
    return HousePrediction(prediction=predictions[0])

@sub_application_housing_predict.post("/bulk-predict", response_model=BulkHousePrediction)
@cache(expire=3600)
async def bulk_predict(request_data: BulkHousePredictionRequest) -> BulkHousePrediction:
	predictions = await multi_predict(request_data.houses)
	return BulkHousePrediction(predictions=predictions)

@sub_application_housing_predict.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}

@sub_application_housing_predict.get("/health")
async def health():
    return {"time": datetime.now()}
