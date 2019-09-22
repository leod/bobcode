#!/bin/bash

name=train_java

CUDA_VISIBLE_DEVICES= onmt-main infer \
  --model $(dirname $0)/model/gpt_2.py \
  --config $(dirname $0)/train.yml $(dirname $0)/data_java.yml $(dirname $0)/$name.yml $(dirname $0)/infer_sampling30.yml \
  --features_file $(dirname $0)/../data/work/java/data/test.sample-prefixes.java.pp.bpe
