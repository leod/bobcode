#!/usr/bin/env python3
"""
Randomly sample chunks of training data from a concatenated corpus.

The concatenated corpus is read from stdin into memory before sampling. Generated
samples are written to stdout line-by-line, with a fixed size. Samples do not cross
files.

This script is kind of a hack to work around the fact that OpenNMT-tf does not have
an implementation of sampling chunks while training.
"""

import sys
import argparse
import random

EOF_SYMBOL = '▗'

def read_words_and_lengths(f):
  words = []
  lengths = []

  n_read = 0
  for line in f:
    for word in line.strip().split(' '):
      words.append(word)
      lengths.append(None)

      if word == EOF_SYMBOL:
        i = len(words)-1
        length = 1
        while i >= 0 and lengths[i] is None:
          lengths[i] = length
          length += 1
          i -= 1

    n_read += 1
    if n_read % 1000000 == 0:
      sys.stderr.write('[{}M]\n'.format(n_read // 1000000))

  return words, lengths

def sample(words, lengths, sample_size):
  assert len(words) >= sample_size

  while True:
    index = random.randint(0, len(words)-1)

    if lengths[index] is not None and lengths[index] >= sample_size:
      return words[index:index+sample_size]

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--sample_size', type=int, required=True, help='Number of words in a sample (chunk).')
  parser.add_argument('--num_samples', type=int, required=True, help='Number of samples (i.e. lines) to generate.')
  parser.add_argument('--eof_symbol', default=EOF_SYMBOL,
      help='Delimiter for files in the concatenated training data. (Default: {})'.format(EOF_SYMBOL))

  args = parser.parse_args()

  sys.stderr.write('Reading from stdin...')
  words, lengths = read_words_and_lengths(sys.stdin)

  sys.stderr.write('Generating samples...')
  n_gen = 0
  for _ in range(args.num_samples):
    s = sample(words, lengths, args.sample_size)

    sys.stdout.write(' '.join(s))
    sys.stdout.write('\n')

    n_gen += 1
    if n_gen % 1000000 == 0:
      sys.stderr.write('[{}M]\n'.format(n_gen // 1000000))

  #for (word, length) in zip(words, lengths):
  #  sys.stdout.write('{}\t{}\n'.format(word, length))

  args = parser.parse_args()

