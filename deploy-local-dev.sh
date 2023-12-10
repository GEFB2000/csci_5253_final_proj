#!/bin/sh

# setting up minio
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install -f minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio
sleep 5

# deploy minio (up before rest)
kubectl apply -f minio/minio-external-service.yaml
sleep 5

# setting up redis (want before rest)
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
sleep 3

# deploying rest server (connects to minio & redis)
kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
sleep 5

# deploy worker.py
kubectl apply -f worker/worker-deployment.yaml

# setting up ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
sleep 5

# setting up rest ingress (keep running until it works- outside of the script)
kubectl apply -f rest/rest-ingress.yaml
sleep 3

# forwarding ports (redis/rest/minio)
kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
kubectl port-forward --address 0.0.0.0 service/rest 5000:5000 &
kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9000:9000 &