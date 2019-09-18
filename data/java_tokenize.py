#!/usr/bin/env python3

import sys
import javalang

SPACE_SYMBOL = '▁'
NEWLINE_SYMBOL = '▏'
EOF_SYMBOL = '▗'

def replace_consecutive(s, x, y, y_after):
  i = 0
  new_s = ''
  start = None
  was_newline = False

  while i < len(s):
    if s[i] == x and start is None:
      start = i
      was_newline = (i == 0 or s[i-1] == '\n')
    elif start is not None:
      if s[i] != x:
        if not was_newline:
          new_s += ' '
        new_s += y * (i - start) + y_after + s[i]
        start = None
    else:
      new_s += s[i]

    i += 1

  return new_s

with open(sys.argv[1]) as f:
  prev_line = 1
  prev_column = 1
  for tok in javalang.tokenizer.tokenize(f.read()):
    num_newlines = tok.position[0] - prev_line
    if num_newlines > 0:
      sys.stdout.write(NEWLINE_SYMBOL * num_newlines)
      sys.stdout.write('\n')
      prev_column = 1
    prev_line = tok.position[0] + tok.value.count('\n')

    num_spaces = tok.position[1] - prev_column
    if num_spaces > 0:
      sys.stdout.write(SPACE_SYMBOL * num_spaces)
      sys.stdout.write(' ')
    prev_column = tok.position[1] + len(tok.value)

    # Join consecutive space symbols or newline symbols into a single word
    text = tok.value

    text = replace_consecutive(text, x=' ', y=SPACE_SYMBOL, y_after=' ')
    text = replace_consecutive(text, x='\n', y=NEWLINE_SYMBOL, y_after='\n')

    sys.stdout.write(text.strip(' '))
    sys.stdout.write(' ')

sys.stdout.write(EOF_SYMBOL)
