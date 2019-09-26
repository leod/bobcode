# Adapted from:
#    https://github.com/OpenNMT/OpenNMT-tf/blob/master/config/models/gpt_2.py

import numpy as np
import opennmt as onmt
import tensorflow as tf

import sys

from opennmt.utils import misc

def gelu(x):
  """Gaussian Error Linear Unit activation function described in
  https://arxiv.org/abs/1606.08415.
  """
  return 0.5 * x * (1 + tf.tanh(np.sqrt(2 / np.pi)
    * (x + 0.044715 * tf.pow(x, 3))))

class GPT2Small(onmt.models.LanguageModel):
  """GPT-2 language model (small version) as described in:
  https://d4mucfpksywv.cloudfront.net/better-language-models/language-models.pdf
  """

  def __init__(self):
    super(GPT2Small, self).__init__(
        decoder=onmt.decoders.SelfAttentionDecoderV2(
            num_layers=12,
            num_units=768,
            num_heads=12,
            ffn_inner_dim=3072,
            ffn_activation=gelu,
            position_encoder=onmt.layers.PositionEmbedder(maximum_position=1024),
            num_sources=0),
        embedding_size=768)
    self.examples_inputter = ChunkedLanguageModelInputter(
        "vocabulary",
        embedding_size=768)

  def auto_config(self, num_devices=1):
    config = super(GPT2Small, self).auto_config(num_devices=num_devices)
    return misc.merge_dict(config, {
        "params": {
            "average_loss_in_time": True,
            "optimizer": "AdamOptimizer",
            "learning_rate": 2.5e-4,
            "decay_type": "cosine_annealing",
            "decay_params": {
                "max_step": 1000000,
                "warmup_steps": 2000,
            }
        },
        "train": {
            "bucket_width": 1,
            # Below options are from GPT-1.
            "batch_size": 64,
            "maximum_features_length": 512
        }
    })

  def _call(self, features, labels, params, mode):
    if mode == tf.estimator.ModeKeys.PREDICT:
      #features['ids'] = tf.Print(features['ids'], [tf.shape(features['ids']), features['ids']], summarize=1000)
      features = {
          "tokens": tf.concat([[[onmt.constants.START_OF_SENTENCE_TOKEN]], features["tokens"]], 1),
          "ids": tf.concat([[[onmt.constants.START_OF_SENTENCE_ID]], features["ids"]], 1),
          "length": features["length"]+1
      }
    return super(GPT2Small, self)._call(features, labels, params, mode)

# Special case the language model inputter so that examples do not end with
# </s>. We need to do this because we train on (almost) fixed size examples of
# 512 symbols each, sampled from larger sequences, similarly to GPT-2. We do
# not want to train the model to predict </s> after exactly 512 tokens.
#
# For example, given a chunk "a bbb c", the features/labels look like this:
# - features: <s> a bbb
# - labels: a bbb c
class ChunkedLanguageModelInputter(onmt.models.language_model.LanguageModelInputter):
  def _generate_example(self, element, training=None):
    labels = self.make_features(element, training=training)
    labels["ids_out"] = labels["ids"]
    del labels["ids"]

    features = {
        "tokens": tf.concat([[onmt.constants.START_OF_SENTENCE_TOKEN], labels["tokens"][:-1]], 0),
        "ids": tf.concat([[onmt.constants.START_OF_SENTENCE_ID], labels["ids_out"][:-1]], 0),
        "length": tf.identity(labels["length"])
    }

    #features["tokens"] = tf.Print(features["tokens"],
    #    [tf.shape(features["tokens"]), tf.shape(labels["tokens"]), features["tokens"], labels["tokens"]],
    #    message='features',
    #    summarize=1000)
    #features["ids"] = tf.Print(features["ids"],
    #    [tf.shape(features["ids"]), tf.shape(labels["ids_out"]), features["ids"], labels["ids_out"]],
    #    message='features',
    #    summarize=1000)

    return features, labels

def model():
  return GPT2Small()
