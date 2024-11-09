# Short Answer Questions

## What are the benefits of caching?

Caching in our application provides significant performance benefits by storing previously computed predictions, eliminating the need for repeated model inference on identical inputs. This reduces computational overhead, decreases response times, and improves overall system efficiency by serving cached results immediately rather than rerunning the machine learning model. This helps yield better resource utilization, reduced server load, and improved scalability of the application, which is especially noticeable in scenarios with repeated requests or bulk predictions.

## What is the difference between Docker and Kubernetes?

While Docker is a container runtime that focuses on building and running individual containers by packaging applications with their dependencies in isolated environments, Kubernetes is a container orchestration platform that manages multiple containers across a cluster of machines. Docker operates at the container level, handling the creation and execution of containers, while Kubernetes operates at a higher level. It manages container deployment, scaling, networking, load balancing, and providing features like automatic failover, service discovery, and rolling updates across an entire distributed system.

## What does a kubernetes `deployment` do, how is this different from a `service`?

A kubernetes deployment manages the lifecycle of pods (containers), ensuring a specified number of replicas are running, handling rolling updates and rollbacks, and maintaining the desired state of the application, while a Service provides a stable networking interface to access these pods, acting as a load balancer and providing a consistent IP address or DNS name that remains unchanged even as pods are created, destroyed, or moved around in the cluster. In essence, Deployments handle the application's runtime aspects while Services manage how other components communicate with that application.

## In our simplified use case, why should we only have 1 redis replica instead of 3?

For this application, it's best to only use a single redis replica because redis is a stateful service maintaining cached data, and multiple replicas would introduce complexity around data consistency and synchronization without providing significant benefits for the caching use case. Since the cache for this lab is used only for performance optimization and can be rebuilt if lost, by computing predictions again, the added complexity of managing multiple redis replicas and ensuring their data consistency outweighs the limited benefits of high availability, making a single redis replica the best choice in this case.

