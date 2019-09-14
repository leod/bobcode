#!/usr/bin/env python3
"""
Retrieve a list of GitHub repositories of a given programming language.
"""

import sys
import requests
import argparse
import json
from urllib.parse import quote as urlencode

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--min_stars', type=int, default=1000, help='Minimal number of stars.')
parser.add_argument('--language', required=True, help='Programming language.')
parser.add_argument('--pages', type=int, required=True, help='Number of pages to retrieve.')

args = parser.parse_args()

url_prefix = 'https://api.github.com/search/repositories?q=stars:>={}+language:{}&sort=stars&order=desc' \
  .format(args.min_stars, urlencode(args.language))

for page in range(args.pages):
  url = url_prefix + '&page={}'.format(page+1)

  sys.stderr.write('Getting: {}\n'.format(url))
  response = requests.get(url)

  if response.status_code == 200:
    obj = json.loads(response.text)
    #print(json.dumps(obj, indent=4))

    for item in obj['items']:
      sys.stdout.write(item['ssh_url'])
      sys.stdout.write('\n')

    #sys.stderr.write('Response is incomplete? {}\n'.format(obj['incomplete_results']))
  else:
    sys.stderr.write('Got error code {}'.format(response.status_code))
    sys.exit(1)
