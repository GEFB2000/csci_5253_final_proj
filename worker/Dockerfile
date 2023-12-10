FROM xserrat/facebook-demucs:latest

RUN pip3 install jsonpickle redis minio demucs

WORKDIR /data

COPY worker.py .

ENTRYPOINT [ "python3", "worker.py" ]


