FROM python:3.10-slim-bookworm
LABEL MAINTAINER="geba9152@colorado.edu"

RUN pip3 install jsonpickle flask redis minio

WORKDIR /srv

COPY rest-server.py /srv
CMD ["python3", "rest-server.py"]




