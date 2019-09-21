#!/bin/bash

awk 1 ORS="\n=============================================================\n" \
  | $(dirname $0)/postprocess.sh
