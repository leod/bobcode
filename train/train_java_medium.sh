#!/bin/bash

name=train_java_medium

mkdir -p $name
onmt-main train \
  --model $(dirname $0)/model/gpt_2_medium.py \
  --config $(dirname $0)/train_medium.yml $(dirname $0)/data_java.yml $(dirname $0)/$name.yml \
  2>&1 | tee -a $name/train.log
