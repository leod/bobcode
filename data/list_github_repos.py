#!/usr/bin/env python3
"""
Retrrieve a list of GitHub repositories of a given programming language.
"""

import sys
import requests
import argparse
import json
from urllib.parse import quote as urlencode

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--min_stars', type=int, default=1000, help='Minimal number of stars.')
parser.add_argument('--language', required=True, help='Programming language.')

args = parser.parse_args()

url = 'https://api.github.com/search/repositories?q=stars:>={}+language:{}&sort=stars&order=desc' \
  .format(args.min_stars, urlencode(args.language))

sys.stderr.write('Getting: {}\n'.format(url))

response = requests.get(url)

if response.status_code == 200:
  sys.stdout.write(response.text)
  obj = json.loads(response.text)

  for item in obj['items']:
    sys.stdout.write(item['ssh_url'])
    sys.stdout.write('\n')

  sys.stderr.write('Response is incomplete? {}\n'.format(obj['incomplete_results']))
else:
  sys.stderr.write('Got error code {}'.format(response.status_code))
  sys.exit(1)
