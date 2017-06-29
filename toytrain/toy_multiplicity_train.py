#IMPORT NECESSAROAY PACKAGESOA
import os,sys
from toy_config import toy_config
#
# Define constants
#
cfg = toy_config()
if not cfg.parse(sys.argv):
  print '[ERROR] Configuraion failure!'
  print 'Exiting...'
  sys.exit(1)

# Check if log directory already exists
if os.path.isdir(cfg.LOGDIR):
  print '[ERROR] Log directory already present:',cfg.LOGDIR
  print 'Exiting...'
  sys.exit(1)

# Check if chosen network is available
try:
  cmd = 'from toynet import toy_%s' % cfg.ARCHITECTURE
  exec(cmd)
except Exception:
  print 'Architecture',cfg.ARCHITECTURE,'is not available...'
  sys.exit(1)

# Print configuration
print cfg

# ready to import heavy packages
from toynet import toy_lenet
import numpy as np
import tensorflow as tf
from toydata import generate_training_images as make_images

#START ACTIVE SESSION                                             \

sess = tf.InteractiveSession()

#PLACEHOLDERS                                                     \

x = tf.placeholder(tf.float32, [None, 784],name='x')
y_0 = tf.placeholder(tf.float32, [None, 5],name='labels0')
y_1 = tf.placeholder(tf.float32, [None, 5], name = 'labels1')
y_2 = tf.placeholder(tf.float32, [None, 5], name = 'labels2')
y_3 = tf.placeholder(tf.float32, [None, 5], name = 'labels3') 

#RESHAPE IMAGE IF NEED BE                                         \

x_image = tf.reshape(x, [-1,28,28,1])
tf.summary.image('input',x_image,5)

#BUILD NETWORK
net = None
cmd = 'net=toy_%s.build(x_image,cfg.NUM_CLASS)' % cfg.ARCHITECTURE
exec(cmd)


#SOFTMAX
with tf.name_scope('softmax'):
  softmax = tf.nn.softmax(logits=net)

#CROSS-ENTROPY                                                    
yvals = [y_0, y_1, y_2, y_3]
cross_entropy_total = []
totalerr = None
for idx, label in enumerate(yvals):
  with tf.name_scope('cross_entropy%d' % idx):
    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=label, logits=net[idx]))
    cross_entropy_total.append(cross_entropy)
    if totalerr is None:
      totalerr = cross_entropy
    else:
      totalerr += cross_entropy
    tf.summary.scalar('cross_entropy', totalerr)

#CROSS-ENTROPY
#yvals = [y_0, y_1, y_2, y_3]
#cross_entropy_total = []
#totalerr = None
#for idx, label in enumerate(yvals):
  #with tf.name_scope('cross_entropy%d' % idx):
   # cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=label, logits=net[idx])
   # cross_entropy_total.append(cross_entropy)
   # c = np.sum(cross_entropy)
   # print cross_entropy
   # if totalerr is None:
   #   totalerr = c
  #  else:
    #  totalerr += c
   # print cross_entropy_total
   # print totalerr
  #  tf.summary.scalar('cross_entropy', totalerr)


#tominimize = tf.reduce_mean(totalerr)
#TRAINING (RMS OR ADAM-OPTIMIZER OPTIONAL)                        \

with tf.name_scope('train'):
  train_step = tf.train.RMSPropOptimizer(0.0003).minimize(totalerr)

#ACCURACY                                                         \

with tf.name_scope('accuracy'):
  cp0 = tf.equal(tf.argmax(net[0],1), tf.argmax(y_0,1))
  cp1 = tf.equal(tf.argmax(net[1], 1), tf.argmax(y_1, 1))
  cp2 = tf.equal(tf.argmax(net[2], 1), tf.argmax(y_2, 1))
  cp3 = tf.equal(tf.argmax(net[3], 1), tf.argmax(y_3, 1))
  correct_prediction = [cp0, cp1, cp2, cp3]
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

tf.summary.scalar('accuracy', accuracy)

saver= tf.train.Saver()

sess.run(tf.global_variables_initializer())

#MERGE SUMMARIES FOR TENSORBOARD                                  \

merged_summary=tf.summary.merge_all()

#WRITE SUMMARIES TO LOG DIRECTORY LOGS6                           \

writer=tf.summary.FileWriter(cfg.LOGDIR)
writer.add_graph(sess.graph)

#TRAINING                                                         \

for i in range(cfg.TRAIN_ITERATIONS):

    batch = make_images(cfg.TRAIN_BATCH_SIZE,debug=cfg.DEBUG)

    if i%100 == 0:

        s = sess.run(merged_summary, feed_dict={x:batch[0], y_0:batch[1][0], y_1:batch[1][1], y_2:batch[1][2], y_3:batch[1][3]})
        writer.add_summary(s,i)

        train_accuracy = accuracy.eval(feed_dict={x:batch[0], y_0:batch[1][0], y_1:batch[1][1], y_2:batch[1][2], y_3:batch[1][3]})

        print("step %d, training accuracy %g"%(i, train_accuracy))

    sess.run(train_step,feed_dict={x: batch[0], y_0: batch[1][0], y_1:batch[1][1], y_2:batch[1][2], y_3:batch[1][3]})    


    if i%1000 ==0:
        batchtest = make_images(cfg.TEST_BATCH_SIZE,debug=cfg.DEBUG)
        test_accuracy = accuracy.eval(feed_dict={x:batchtest[0], y_0:batchtest[1][0], y_1:batchtest[1][1], y_2:batchtest[1][2], y_3:batchtest[1][3]})
        print("step %d, test accuracy %g"%(i, test_accuracy))

# post training test
batch = make_images(cfg.TEST_BATCH_SIZE,debug=cfg.DEBUG)
print("Final test accuracy %g"%accuracy.eval(feed_dict={x: batch[0], y_0: batch[1][0], y_1:batch[1][1], y_2:batch[1][2], y_3:batch[1][3]}))

# inform log directory
print('Run `tensorboard --logdir=%s` in terminal to see the result\
s.' % cfg.LOGDIR)

# do analysis, if specified
if not cfg.ANA_BATCH_SIZE:
  sys.exit(0)

#fout = open('%s/analysis.csv' % cfg.LOGDIR,'w')
fout.write('entry,label,prediction')
for idx in xrange(cfg.NUM_CLASS):
  fout.write(',score%02d' % idx)
fout.write('\n')

# run analysis
from matplotlib import pyplot as plt
batch    = make_images(cfg.ANA_BATCH_SIZE,debug=cfg.DEBUG)
score_vv = softmax.eval(feed_dict={x: batch[0]})
for entry,score_v in enumerate(score_vv):
  label = int(np.argmax(batch[1][entry]))
  prediction = int(np.argmax(score_v))
  fout.write('%d,%d,%d' % (entry, label, prediction))
  for score in score_v:
    fout.write(',%g' % score)
  fout.write('\n')

  if not label == prediction:
    fig, ax = plt.subplots(figsize = (28,28), facecolor = 'w')
    plt.imshow(np.reshape(batch[0][idx], (28, 28)), interpolation \
= 'none')
    plt.savefig('entry%0d-%d.png' % (idx, label))
    plt.close()

fout.close()