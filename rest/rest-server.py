#!/usr/bin/env python3

# Purpose of rest-server= handles audio-related tasks (responses/requests for lab7)
# 1. managing a Redis queue (for separation of tracks with Demucs)
# 2. interacts with Minio for storing audio data
# !/usr/bin/env python3

from flask import Flask, request, Response
import jsonpickle
import base64
import json
import os
import redis
import io
from minio import Minio

# redis
redis_host = os.getenv("REDIS_HOST") or "redis"
redis_port = os.getenv("REDIS_PORT") or "6379"
redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

# flask
server_host = os.getenv("FLASK_HOST") or "0.0.0.0"
server_port = os.getenv("FLASK_PORT") or "5000"
app = Flask(__name__)

# minio
minioHost = os.getenv("MINIO_HOST") or "minio-proj.minio-ns.svc.cluster.local:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

queue = "queue"
output = "output"

# bucket exists
# Create Queue
if not client.bucket_exists(queue):
    print(f"Create bucket {queue}")
    client.make_bucket(queue)
if not client.bucket_exists(output):
    print(f"Create bucket {output}")
    client.make_bucket(output)


@app.route('/apiv1/separate', methods=['POST'])
def separate():
    print("START SEPARATE")
    r = request
    data = json.loads(r.get_data())
    mp3 = base64.b64decode(data['mp3'])
    length = len(mp3)

    # hash for redis
    # mp3 for minio
    try:
        print(data['callback']['data']['mp3'])
        # redis hash
        name_hash = hash(data['callback']['data']['mp3'])
        redis_connection.rpush('mp3_list', name_hash)
        print("added " + str(name_hash) + " queue")
        # minio bytes
        client.put_object(queue, str(name_hash), io.BytesIO(mp3), length, content_type="audio/mpeg")
        print("added " + str(name_hash) + " queue bucket")


        response = {'message': name_hash}
        response_pickle = jsonpickle.encode(response)
        return Response(response=response_pickle, status=200, mimetype="application/json")

    except Exception as err:
        response = {'message': 'error not pushed', 'details': str(err)}
        response_pickle = jsonpickle.encode(response)
        return Response(response=response_pickle, status=200, mimetype="application/json")


@app.route('/apiv1/queue', methods=['GET'])
def get_queue():
    contents = redis_connection.lrange('mp3_list', 0, -1)
    all_response = []
    for item in contents:
        mp3_hash = jsonpickle.decode(item)
        all_response.append(str(mp3_hash))
    response = {"redis_queue": all_response}
    response_pickle = jsonpickle.encode(response)
    return Response(response=response_pickle, status=200, mimetype="application/json")

app.run(host=server_host, port=server_port)