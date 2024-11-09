# California Housing Price Prediction Service

Final submission folder is lab3.

## Overview
This project implements a machine learning service that predicts California housing prices, deployed as a containerized application using FastAPI and Redis caching on Kubernetes. The service expansion enables bulk prediction endpoints, utilizing a pre-trained scikit-learn model for making predictions about house prices based on features like median income, house age, and geographic location.

## Key Components
- **FastAPI Framework**: Provides a high-performance web API with automatic OpenAPI documentation
- **Redis Caching**: Improves performance by storing prediction results for repeated queries
- **Kubernetes Deployment**: Ensures scalable and reliable service operation with health monitoring
- **Docker Containerization**: Packages the application and its dependencies for consistent deployment
- **Machine Learning Model**: Uses scikit-learn to predict housing prices based on input features

## Architecture
The application is structured as a microservice architecture with two main components:
1. **API Service**: Three replicas handling HTTP requests and model predictions
2. **Redis Cache**: Single instance storing prediction results for improved performance

The service is deployed to Kubernetes with proper resource limits and init containers ensuring dependencies are available before startup. FastAPI-Cache2 handles the caching layer, storing predictions with a "w255-cache-prediction" prefix for easy identification. The API deployment has 3 replicas. Only 1 redis replica is defined for this deployment, and the rationale for this is explained in the SHORT-ANSWER.md. 

## Features
- Single and bulk prediction endpoints with input validation
- Efficient vectorized predictions for multiple houses
- Automatic caching of prediction results
- Health monitoring and readiness checks
- Geographic coordinate validation
- Kubernetes-native deployment with proper resource management


Tests added for the expanded functionality follow this structure and are in test_src.py along with tests from the previous lab: 
def test_my_test_that_uses_lifespanned_client():
    with TestClient(app) as lifespanned_client:
        response = lifespanned_client.post(...)

## API Endpoints
- `POST /lab/predict`: Single house price prediction
- `POST /lab/bulk-predict`: Multiple house price predictions
- `GET /lab/health`: Service health check

## Development & Dependencies
The project uses modern development practices including:
- Poetry for dependency management
- FastAPI for API development
- Docker for containerization
- Kubernetes for orchestration
- Pytest for automated testing
- Dependencies:

[tool.poetry.dependencies]
python = "~3.11"
fastapi = {version = "^0.112.2", extras = ["standard"]}
fastapi-cache2 = {version = "0.1.9", extras = ["redis"]}
redis = ">=4.2.0rc1,<5.0.0"
joblib = "1.4.2"
scikit-learn = "1.5.2"

[tool.poetry.group.dev.dependencies]
ruff = "^0.6.2"
pytest = "^8.3.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

## Prerequisites
- Minikube installed
- kubectl installed
- Docker installed
- Python 3.11 with Poetry

## Initial directions cloning and running with Minikube: 

Clone the repository: git clone https://github.com/UCB-W255/lab-3-caching-and-kubernetes-tssccttr/tree/main/lab3-caching-and-kubernetes

1. Start Minikube
```bash
minikube start
```

2. Build Docker Image
```bash
# Build the API image
docker build -t lab3:latest .

# Load into Minikube
minikube image load lab3:latest
```

3. Deploy Applications
```bash
# Create namespace
kubectl apply -f namespace.yaml

# Deploy Redis
kubectl apply -f deployment-redis.yaml --namespace=w255
kubectl apply -f service-redis.yaml --namespace=w255

# Deploy API
kubectl apply -f deployment-pythonapi.yaml --namespace=w255
kubectl apply -f service-prediction.yaml --namespace=w255
```

4. Verify Deployment
```bash
# Check pod status
kubectl get pods -n w255

# Check services
kubectl get services -n w255
```

5. Access the API
```bash
# Get service URL
minikube service lab3api-service --url --namespace=w255
```
6. Cleanup
```bash
kubectl delete namespace w255
minikube stop
```

 