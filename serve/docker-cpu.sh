#!/bin/bash

if [ ! "$#" -eq 2 ]; then
  echo "Usage: $0 <model> <port>"
  exit 1
fi

MODEL=$1
PORT=$2

echo "Serving model at path '$MODEL' on port $PORT"
echo "Starting docker..."

docker run \
  --rm \
  -p $PORT:$PORT \
  -v "$MODEL":/model \
  --name bobcode \
  --entrypoint tensorflow_model_server \
  tensorflow/serving:1.11.0 \
    --port=$PORT \
    --model_base_path=/model \
    --model_name=bobcode
