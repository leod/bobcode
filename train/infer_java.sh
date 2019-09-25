#!/bin/bash

MODE=${MODE:-sampling4}
TEST=${TEST:-"$(dirname $0)/../data/work/java/data/test.sample-prefixes.java.pp.bpe"}

name=train_java

PYTHONPATH=$(dirname $0)/../../OpenNMT-tf CUDA_VISIBLE_DEVICES= python3 $(dirname $0)/../../OpenNMT-tf/opennmt/bin/main.py infer \
  --model $(dirname $0)/model/gpt_2.py \
  --config $(dirname $0)/train.yml $(dirname $0)/data_java.yml $(dirname $0)/$name.yml $(dirname $0)/infer_$MODE.yml \
  --features_file "$TEST"
