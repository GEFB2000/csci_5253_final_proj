import redis
import subprocess
import os
from minio import Minio

print("worker start")

# redis
redis_host = os.getenv("REDIS_HOST") or "localhost"
redis_port = os.getenv("REDIS_PORT") or "6379"
redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

# minio
minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
   secure=False,
   access_key=minioUser,
   secret_key=minioPasswd)

queue = "queue"
output = "output"

while True:
    # queue
    mp3 = redis_connection.blpop('mp3_list')
    print(mp3[1])
    mp3_hash = mp3[1]

    print(f"processing {mp3_hash}")
    # queue bucket mp3 hash
    client.fget_object(queue, mp3_hash, f"/data/input/{mp3_hash}")

    result = os.system(f"python3 -m demucs -d cpu --out /data/output --mp3 /data/input/{mp3_hash} ")

    if result == 0:
        print("executed track is separated")
    else:
        print(f"error {result}")

    client.fput_object(output, f"bass_{mp3_hash}.mp3", "/data/output/mdx_extra_q/"+str(mp3_hash)+"/bass.mp3")
    client.fput_object(output, f"vocal_{mp3_hash}.mp3", "/data/output/mdx_extra_q/"+str(mp3_hash)+"/vocals.mp3")
    client.fput_object(output, f"drums_{mp3_hash}.mp3", "/data/output/mdx_extra_q/"+str(mp3_hash)+"/drums.mp3")
    client.fput_object(output, f"other_{mp3_hash}.mp3", "/data/output/mdx_extra_q/"+str(mp3_hash)+"/other.mp3")




