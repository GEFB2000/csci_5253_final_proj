# This is just a reference script for me to have code to build/push my dockerfiles
# all dockerfiles here are done in commandline for ease

docker build -t gefb2000/demucs-rest rest/.
docker push gefb2000/demucs-rest


docker build -t gefb2000/demucs-cpu .
docker push gefb2000/demucs-cpu

