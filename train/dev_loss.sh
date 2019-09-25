#!/bin/bash

awk -F '\\|\\|\\|' '/\|\|\|/ { s+=$1; m=split($2,a," "); n+=m; } END { print s / n }'
