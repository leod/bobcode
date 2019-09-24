#!/bin/bash

MODE=${MODE:-sampling4}
TEST=${TEST:-"$(dirname $0)/../data/work/java/data/test.sample-prefixes.java.pp.bpe"}

name=train_java

CUDA_VISIBLE_DEVICES= onmt-main infer \
  --model $(dirname $0)/model/gpt_2.py \
  --config $(dirname $0)/train.yml $(dirname $0)/data_java.yml $(dirname $0)/$name.yml $(dirname $0)/infer_$MODE.yml \
  --features_file "$TEST"
