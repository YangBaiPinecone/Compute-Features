'''
   File that computes features for a set of images

   ex. python compute_features.py --data_dir=/mnt/images/ --model=vgg19 --model_path=./vgg_19.ckpt

'''

import tensorflow as tf
import scipy.misc as misc
import cPickle as pickle
from tqdm import tqdm
import numpy as np
import argparse
import fnmatch
import sys
import os

sys.path.insert(0, 'nets/')

slim = tf.contrib.slim

'''

   Recursively obtains all images in the directory specified

'''
def getPaths(data_dir):
      
   image_paths = []

   # add more extensions if need be
   ps = ['jpg', 'jpeg', 'JPG', 'JPEG', 'bmp', 'BMP', 'png', 'PNG']
   for p in ps:
      pattern   = '*.'+p
      for d, s, fList in os.walk(data_dir):
         for filename in fList:
            if fnmatch.fnmatch(filename, pattern):
               fname_ = os.path.join(d,filename)
               image_paths.append(fname_)
   return image_paths

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('--data_dir', required=True, type=str, help='Directory images are in. Searches recursively.')
   parser.add_argument('--model', required=True, type=str, help='Model to use')
   parser.add_argument('--checkpoint_file', required=True, type=str, help='Model file')
   a = parser.parse_args()

   data_dir        = a.data_dir
   model           = a.model
   checkpoint_file = a.checkpoint_file
   
   if model == 'inception_v1': height, width, channels = 224, 224, 3
   if model == 'vgg19':        height, width, channels = 224, 224, 3

   x = tf.placeholder(tf.float32, shape=(1, height, width, channels))
   
   # load up model specific stuff
   if model == 'inception_v1':
      from inception_v1 import *
      arg_scope = inception_v1_arg_scope()
      with slim.arg_scope(arg_scope):
         logits, end_points = inception_v1(x, is_training=False, num_classes=1001)
         features = end_points['AvgPool_0a_7x7']
   elif model == 'vgg19':
      from vgg import *
      arg_scope = vgg_arg_scope()
      with slim.arg_scope(arg_scope):
         logits, end_points = vgg_19(x, is_training=False)
         features = end_points['vgg_19/fc8']

   sess  = tf.Session()
   saver = tf.train.Saver()
   saver.restore(sess, checkpoint_file)

   feat_dict = {}
   paths = getPaths(data_dir)
   print 'Computing features...'
   for path in tqdm(paths):
      image = misc.imread(path)
      image = misc.imresize(image, (height, width))
      image = np.expand_dims(image, 0)
      feat = np.squeeze(sess.run(features, feed_dict={x:image}))
      feat_dict[path] = feat

   exp_pkl = open(model+'_features.pkl', 'wb')
   data = pickle.dumps(feat_dict)
   exp_pkl.write(data)
   exp_pkl.close()
