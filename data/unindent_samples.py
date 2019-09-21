#!/usr/bin/env python3

import sys
import random

SPACE_SYMBOL = '▁'
NEWLINE_SYMBOL = '▏'

def prefix_length(char, string):
  assert len(char) == 1

  length = 0
  i = 0
  while i < len(string) and string[i] == char:
    length += 1
    i += 1

  return length

def unindent_sample(sample):
  lines = sample.split(NEWLINE_SYMBOL)

  line_starts = [0]
  line_ends = []
  was_newline = False

  for i, c in enumerate(sample):
    if c != NEWLINE_SYMBOL and was_newline:
      was_newline = False
      line_starts.append(i)

      if i != 0:
        line_ends.append(i)
    elif c == NEWLINE_SYMBOL:
      was_newline = True

  line_ends.append(len(sample))

  assert len(line_starts) == len(line_ends)

  indents = [
    prefix_length(SPACE_SYMBOL, sample[line_starts[i]:line_ends[i]].strip())
    for i in range(len(line_starts))
  ]

  if len(indents) <= 1:
    return None

  min_succ = min(indents[1:])

  if min_succ == 0:
    return None
  if indents[0] < min_succ and indents[0] != 0:
    return None

  result = ''
  for start, end, indent in zip(line_starts, line_ends, indents):
    unindent = min_succ if indent >= min_succ else 0
    result += sample[start:end].strip()[unindent:]
    result += ' '

  return result + '\n'

if __name__ == '__main__':
  percent = int(sys.argv[1])

  sys.stderr.write('Will attempt to unindent {}% of samples\n'.format(percent))

  n_done = 0
  n_unindented = 0

  for sample in sys.stdin:
    if random.randint(0, 99) < percent:
      unindented = unindent_sample(sample)
      if unindented:
        sys.stdout.write(unindented)
        n_unindented += 1
      else:
        sys.stdout.write(sample)
    else:
      sys.stdout.write(sample)

    n_done += 1

  sys.stderr.write('Done. Unindented {} lines out of {} ({:.2f}%)\n'
      .format(n_unindented, n_done, float(n_unindented) / n_done * 100.0))
