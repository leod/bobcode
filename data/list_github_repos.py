#!/usr/bin/env python3
"""
Retrieve a list of GitHub repositories of a given programming language.

The output is written to stdout in two columns, where the first column
is the SSH clone url and the second column is the default branch.
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
parser.add_argument('--first_page', type=int, default=1, help='First page to retrieve.')

args = parser.parse_args()

url_prefix = 'https://api.github.com/search/repositories?q=stars:>={}+language:{}&sort=stars&order=desc' \
  .format(args.min_stars, urlencode(args.language))

for page in range(args.first_page-1, args.pages):
  url = url_prefix + '&page={}'.format(page+1)

  sys.stderr.write('Getting: {}\n'.format(url))
  response = requests.get(url)

  if response.status_code == 200:
    obj = json.loads(response.text)
    #print(json.dumps(obj, indent=4))

    for item in obj['items']:
      sys.stdout.write('{}\t{}\n'.format(item['ssh_url'], item['default_branch']))

    #sys.stderr.write('Response is incomplete? {}\n'.format(obj['incomplete_results']))
  else:
    sys.stderr.write('Got error code {}'.format(response.status_code))
    sys.exit(1)
