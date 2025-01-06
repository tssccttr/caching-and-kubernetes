
# Caching and Kubernetes

## Overview

-  API takes a *list* of inputs to predict instead of a single input.
-  API will have a rudimentary Redis cache for the new `/bulk-predict` endpoint based on the inputs.
-  Application deploys locally on a Kubernetes environment (Minikube).


### API Requirements

- [ ] Ensure the model is loaded only when the container is instantiated/started (i.e., not every time you run a prediction)
- [ ] Create a new request model which extends your single input model to accept a list of inputs instead of a single input.
  - Use `houses` as the field name which expects a list of the input objects you designed in lab2
- [ ] Create a response model returning a `list` of floats
- [ ] Create a new `POST` endpoint `/bulk-predict` which takes a `List` of inputs based on the request model you created above
  - You must utilize the `multi_predict` function we have defined for you in the template
  - Add the decorator key to this defined function
- [ ] Run your predictions on a matrix input instead of row by row. (See [Input Vectorization](#input-vectorization) for our expectations)
- [ ] Cache the entire input sent to `/predict` to Redis (See [Redis Expectations](#redis-expectations) for our expectations)
- [ ] Cache the entire input sent to `/bulk-predict` to Redis (See [Redis Expectations](#redis-expectations) for our expectations)
- [ ] Update your tests from `lab2` to give list inputs to your new endpoint

### Deployment Requirements

- [ ] Deploy your application to Kubernetes locally (Minikube)
  - [ ] (`namespace.yaml`) Deploy all components to a non-default `namespace` called `w255`
  - [ ] (`deployment-redis.yaml`) Deployment for Redis in `w255` namespace
    - See [Redis Expectations](#redis-expectations) for more details and requirements
  - [ ] (`deployment-pythonapi.yaml`) Deployment for your API in `w255` namespace
    - [ ] Your API deployment (`deplyoment-pythonapi.yaml`) should include an `initContainer`, `readinessProbe`, `livenessProbe`, and `startupProbe`
      - Init Containers:
        - [ ] Create an `initContainer` named `init-verify-redis-service-dns` should wait for the Redis DNS to become available
        - [ ] Create an `initContainer` named `init-verify-redis-ready` should wait for the Redis Service to become available
      - [ ] `readinessProbe` should wait for the API to be locally available by using the `/health` endpoint
      - [ ] `livenessProbe` should monitor whether the API is responsive by using the `/health` endpoint
      - [ ] `startupProbe` should wait for the API to be locally available by using the `/health` endpoint
    - [ ] Your API deployment should have `3` replicas
  - [ ] (`service-redis.yaml`) Service for Redis in `w255` namespace
  - [ ] (`service-prediction.yaml`) Service for API in `w255` namespace
    - It should be a [LoadBalancer](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) type

### API Diagram

The following is a visualization of the sequence diagram describing our new API

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant A as API
    participant R as Redis
    participant M as Model

    U ->> A: POST JSON payload
    break Input payload does not satisfy pydantic schema
        A ->> U: Return 422 Error
    end
    A ->> R: Check if value is<br>already in cache
    alt Value exists in cache
        R ->> A: Return cached<br>value to app
    else Value not in cache
        A ->>+ M: Input values to model
        M ->>- A: Store returned values
        A ->> R: Store returned value<br>in cache
    end

    A ->> U: Return Values as<br>output data model
```

### Deployment Diagram

The following is a visualization of the infrastructure you should implement for Lab 3.

```mermaid
flowchart TB
User(User)
    subgraph k8s [Minikube Node]
    subgraph subgraph_padding1 [ ]
        subgraph cn [Common namespace: w255]
            direction TB
            subgraph subgraph_padding2 [ ]
            NPS2(LoadBalancer: prediction-service):::nodes
            subgraph PD [python-api-deployment]
                direction TB
                IC1(Init Container: init-verify-redis-service-dns)
                IC2(Init Container: init-verify-redis-ready)
                FA(Fast API Container):::fa

                IC1 --> IC2 --> FA
            end
            NPS1(ClusterIP: redis-service):::nodes
            RD(redis-deployment)

            NPS1 <-->|Port 6379| PD
            NPS1 <-->|Port 6379| RD
            NPS2 <-->|Port 8000| PD
        end
        end
    end
    end

User <---->|Minikube Tunnel or Port Forward <br/> Port:8000| NPS2

classDef nodes fill:#68A063
classDef subgraph_padding fill:none,stroke:none
classDef inits fill:#AF5FEE
classDef fa fill:#009485

style cn fill:#B6D0E2
style RD fill:#D82C20
style PD fill:#FFD43B
style k8s fill:#326ce5;

class subgraph_padding1,subgraph_padding2 subgraph_padding
class IC1,IC2 inits
```


## Time Expectations

This lab will take approximately ~20 hours. Most of the time will be spent configuring Kubernetes, the deployment, and services, followed by testing to ensure everything is working correctly. Minimal changes to the API are required.
