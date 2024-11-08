import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from joblib import load
from redis import asyncio
from datetime import datetime
from typing import List
import numpy as np

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
    HOST_URL = os.getenv("REDIS_URL", LOCAL_REDIS_URL)
    redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)

    # We initialize the connection to Redis and declare that all keys in the
    # database will be prefixed with w255-cache-predict. Do not change this
    # prefix for the submission.
    FastAPICache.init(RedisBackend(redis), prefix="w255-cache-prediction")

    yield
    # We don't need a shutdown event for our system, but we could put something
    # here after the yield to deal with things during shutdown
    logging.info("Shutting down Lab3 API")

class House(BaseModel):
    """Data model to parse the request body JSON for a single house."""
    model_config = ConfigDict(extra="forbid")

    MedInc: float = Field(gt=0)
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

    def to_np(self):
        return np.array(list(vars(self).values())).reshape(1, 8)

class BulkHousePredictionRequest(BaseModel):
    """Data model for bulk prediction requests."""
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
@cache(expire=3600)
async def multi_predict(houses_data: List[House]) --> List[float]:
    
    # vectorized predictions on multiple house inputs, returns ist of predicted house prices
    if not houses_data:
        return []
    
    # converting to array for vectorized prediction
    input_matrix = np.array([list(vars(house).values()) for house in houses_data])
    predictions = model.predict(input_matrix).tolist()
    return predictions

@sub_application_housing_predict.post("/predict", response_model=HousePrediction)
async def predict(house: House, request: Request):
    # raw input for caching
    raw_input = await request.json()
    
    # making prediction using the globally loaded model
    predict_value = float(model.predict(house.to_np())[0])
    
    # storing prediction in cache 
    FastAPICache.set(f"prediction:{raw_input}", 
                    {"input": raw_input, "prediction": predict_value, 
                     "timestamp": datetime.now().isoformat()})
    
    return HousePrediction(prediction=predict_value)

@sub_application_housing_predict.post("/bulk-predict", response_model=BulkHousePrediction)
async def bulk_predict(request_data: BulkHousePredictionRequest, request: Request):
    # raw input for caching
    raw_input = await request.json()
    
    # using multi_predict function for vectorized predictions
    predictions = await multi_predict(request_data.houses)
    
    # store bulk prediction in cache 
    FastAPICache.set(f"bulk-prediction:{raw_input}", 
                    {"input": raw_input, "predictions": predictions, 
                     "timestamp": datetime.now().isoformat()})
    
    return BulkHousePrediction(predictions=predictions)

@sub_application_housing_predict.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}

@sub_application_housing_predict.get("/health")
async def health():
    return {"time": datetime.now()}
