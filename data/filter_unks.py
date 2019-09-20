#!/usr/bin/env python3

import sys

voc = set()
with open(sys.argv[1]) as f_voc:
  for line in f_voc:
    voc.add(line.strip())

n_done = 0
n_filtered = 0

for line in sys.stdin:
  toks = line.strip().split()

  keep = True
  for tok in toks:
    if tok not in voc:
      keep = False
      break

  if keep:
    sys.stdout.write(line)
  else:
    n_filtered += 1

  n_done += 1
  if n_done % 1000000 == 0:
    sys.stderr.write('[{}M]\n'.format(n_done / 1000000))

sys.stderr.write('Done. Filtered {} lines out of {} ({:.2f}%)\n'
  .format(n_filtered, n_done, float(n_filtered) / n_done * 100.0))
