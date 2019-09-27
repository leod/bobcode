#!/usr/bin/env python3

from flask import Flask, jsonify, request, abort

from serve.client import Generator

app = Flask(__name__, static_url_path='/static')

HOST='localhost'
PORT=9000
MODEL_NAME='bobcode'
BPE_CODES='../data/work/java/data/bpecodes'

generator = Generator(host=HOST,
                      port=PORT,
                      model_name=MODEL_NAME,
                      bpe_codes=BPE_CODES)

@app.route('/gen', methods=['POST'])
def gen():
  if 'context' not in request.form:
    abort(400)

  context = request.form.get('context')

  if len(context) > 2048:
    abort(414)

  hyp = generator(context)
  print(hyp)

  return jsonify(hyp)

@app.route('/')
def index():
  return app.send_static_file('index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=7000)
