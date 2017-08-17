import numpy as np
import tensorflow as tf
import sys
tf.set_random_seed(777)

xy = np.loadtxt('herald_feature_set.en.csv',delimiter=',', dtype=np.float32)

x_data = xy[:,0:-1]
y_data = xy[:,[-1]]

#batch_size = 1000
X = tf.placeholder(tf.float32, shape=[None,10])
Y = tf.placeholder(tf.float32, shape=[None, 1])
W1 = tf.get_variable("W1", shape =[10,1] , initializer=tf.contrib.layers.xavier_initializer())
b1 = tf.Variable(tf.zeros([1]))

hypothesis = tf.sigmoid(tf.matmul(X,W1) + b1)
saver = tf.train.Saver()
predicted = tf.cast(hypothesis > 0.5 , dtype = tf.float32)

with tf.Session() as sess:
	#sess.run(init_op)
	save_path = '.model/sentence_tokenizer.ckpt'
	saver.restore(sess, save_path)
	h, c = sess.run([hypothesis, predicted], feed_dict = {X: x_data, Y: y_data})

label = 0 
machine = 0
for i in range(len(y_data)):
	if y_data[i] == [ 1.]:
		label += 1
		if c[i] == [ 1.]:
			machine +=1
print("label:", label, "machine:", machine, "recall:", machine/label)
machine = 0 
label = 0 
for i in range(len(c)):
	if c[i] == [ 1.]:
		machine += 1
		if y_data[i] == [ 1.]:
			label += 1
print("machine:", machine, "label:", label, "precision:", label/machine)




