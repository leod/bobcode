#!/bin/bash

name=train_java

mkdir -p $name
onmt-main train \
  --model $(dirname $0)/model/gpt_2.py \
  --config $(dirname $0)/train.yml $(dirname $0)/data_java.yml $(dirname $0)/$name.yml \
  2>&1 | tee -a $name/train.log
