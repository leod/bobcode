#!/bin/bash

# Helper script for enabling parallel tokenization with caching.
# Used in `pipeline_java.sh`.

if [ ! -e "$1.pp" ]; then
  PYTHONPATH=$(dirname $0)/javalang $(dirname $0)/java_tokenize.py \
    <(sed -e 's/\t/    /g' -e 's/\r//g' "$1") \
    > "$1.pp"
fi
