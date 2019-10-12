#!/bin/bash

DEV=${TEST:-"$(dirname $0)/../data/work/java/data/dev.samples.java.pp.bpe"}

name=train_java_medium
ckpt=$1

mkdir -p $name/score

PYTHONPATH=$(dirname $0)/../../OpenNMT-tf CUDA_VISIBLE_DEVICES= python3 $(dirname $0)/../../OpenNMT-tf/opennmt/bin/main.py score \
  --model $(dirname $0)/model/gpt_2_medium.py \
  --config $(dirname $0)/train_medium.yml $(dirname $0)/data_java.yml $(dirname $0)/$name.yml $(dirname $0)/score.yml \
  --features_file "$DEV" \
  --checkpoint_path $name/model.ckpt-$ckpt
