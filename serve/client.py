#!/usr/bin/env python3
""" Client for TensorFlow serving. """

# adapted from https://github.com/OpenNMT/OpenNMT-tf/blob/master/examples/serving/ende_client.py
# and from https://github.com/leod/hncynic/blob/master/serve/client.py

import sys
import argparse
from io import StringIO

import grpc
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc

import java_tokenize
import subword_nmt.apply_bpe as apply_bpe

class Generator:
  def __init__(self,
               host,
               port,
               model_name,
               bpe_codes):
    channel = grpc.insecure_channel("%s:%d" % (host, port))
    self.stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    self.model_name = model_name

    with open(bpe_codes) as f:
      self.bpe = apply_bpe.BPE(f)

  def preprocess(self, context):
    context = context.replace('\t', '    ')

    buf = StringIO(context)
    java_tokenize.tokenize(context, buf)

    tok = buf.getvalue()
    tok = tok.replace(java_tokenize.EOF_SYMBOL, '')
    tok = tok.replace('\n', ' ')
    tok = tok.strip()

    return self.bpe.segment_tokens(tok.split(' '))

  def postprocess(self, hyp):
    hyp = hyp.replace('@@ ', '')
    hyp = hyp.replace(' ', '')
    hyp = hyp.replace(java_tokenize.SPACE_SYMBOL, ' ')
    hyp = hyp.replace(java_tokenize.NEWLINE_SYMBOL, '\n')
    hyp = hyp.replace(java_tokenize.EOF_SYMBOL, '')
    return hyp

  def __call__(self, context, timeout=50.0):
    context_pp = self.preprocess(context)

    request = predict_pb2.PredictRequest()
    request.model_spec.name = self.model_name
    request.inputs['tokens'].CopyFrom(
      tf.make_tensor_proto(context_pp, shape=(1, len(context_pp))))
    request.inputs['length'].CopyFrom(
      tf.make_tensor_proto([len(context_pp)], shape=(1,)))

    result = self.stub.Predict.future(request, timeout).result()

    predictions = tf.make_ndarray(result.outputs["tokens"])[:, 1:]

    hyp = ' '.join([token.decode('utf-8') for token in predictions[0]])

    return self.postprocess(hyp)

def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--host', default='localhost', help='model server host')
  parser.add_argument('--port', type=int, default=9000, help='model server port')
  parser.add_argument('--model_name', required=True, help='model name')
  parser.add_argument('--bpe_codes', required=True, help='BPE codes')

  args = parser.parse_args()
 
  generator = Generator(host=args.host,
                        port=args.port,
                        model_name=args.model_name,
                        bpe_codes=args.bpe_codes)

  context = sys.stdin.read()
  hyp = generator(context)
  sys.stdout.write(hyp)
  
if __name__ == "__main__":
  main()
