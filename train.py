import numpy as np
import tensorflow as tf
import os

import model
import inputs 
import time
import initializer

FLAGS = tf.app.flags.FLAGS

TRAIN_DIR = "./checkpoints/run_0"

def train():
  """Train ring_net for a number of steps."""
  with tf.Graph().as_default():
    # global step counter
    global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

    # make inputs mineral
    image_train, label_train = inputs.inputs_mineral(FLAGS.batch_size, train=True)
    #image_test,  label_test  = inputs.inputs_mineral(FLAGS.batch_size, train=False)

    # create network train
    logit_train = model.inference(image_train, keep_prob=0.8)
    #logit_test  = model.inference(image_test,  keep_prob=1.0, is_training=False)

    # calc error mineral
    loss_train = model.loss(label_train, logit_train)
    #loss_test  = model.loss_mineral(label_test,  logits_test,  train=False)

    # train hopefuly 
    train_op = model.train(loss_train, FLAGS.learning_rate, global_step)

    # List of all Variables
    variables = tf.global_variables()

    # Build a saver
    saver = tf.train.Saver(tf.global_variables())   
    #for i, variable in enumerate(variables):
    #  print '----------------------------------------------'
    #  print variable.name[:variable.name.index(':')]

    # Summary op
    summary_op = tf.summary.merge_all()
 
    # Build an initialization operation to run below.
    #init = tf.global_variables_initializer()

    # Start running operations on the Graph.
    sess = tf.Session()

    # init if this is the very time training
    initializer.initialize_inception_v3(sess, variables)
    #sess.run(init)
 
    # init from checkpoint
    saver_restore = tf.train.Saver(variables)
    ckpt = tf.train.get_checkpoint_state(TRAIN_DIR)
    if ckpt is not None:
      print("init from " + TRAIN_DIR)
      try:
         saver_restore.restore(sess, ckpt.model_checkpoint_path)
      except:
         tf.gfile.DeleteRecursively(TRAIN_DIR)
         tf.gfile.MakeDirs(TRAIN_DIR)
         print("there was a problem using variables in checkpoint, random init will be used instead")

    # Start que runner
    tf.train.start_queue_runners(sess=sess)

    # Summary op
    graph_def = sess.graph.as_graph_def(add_shapes=True)
    summary_writer = tf.summary.FileWriter(TRAIN_DIR, graph_def=graph_def)

    # calc number of steps left to run
    run_steps = FLAGS.max_steps - int(sess.run(global_step))
    for step in xrange(run_steps):
      current_step = sess.run(global_step)
      t = time.time()
      _, l_train = sess.run([train_op, loss_train])
      elapsed = time.time() - t

      assert not np.isnan(l_train), 'Model diverged with loss = NaN'

      if current_step % 101 == 1:
        print("loss value at " + str(l_train))
        print("time per batch is " + str(elapsed))

      if current_step % 1001 == 1:
        #l_test = sess.run(loss_test)
        summary_str = sess.run(summary_op)
        summary_writer.add_summary(summary_str, current_step) 
        checkpoint_path = os.path.join(TRAIN_DIR, 'model.ckpt')
        saver.save(sess, checkpoint_path, global_step=global_step)  
        print("saved to " + TRAIN_DIR)

def main(argv=None):  # pylint: disable=unused-argument
  train()

if __name__ == '__main__':
  tf.app.run()
