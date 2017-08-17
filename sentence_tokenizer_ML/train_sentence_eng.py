import tensorflow as tf
import numpy as np
tf.set_random_seed(777)  # for reproducibility

xy = np.loadtxt('train_data/train_feature_set.en.csv', delimiter=',', dtype=np.float32)
test = np.loadtxt('donga_feature_set.en.csv',delimiter=',',dtype=np.float32)

x_data = xy[:, 0:-1]
y_data = xy[:, [-1]]

x_test = test[:,0:-1]
y_test = test[:,[-1]]

print(x_data.shape, y_data.shape)

# parameters
learning_rate = 0.07
training_epochs = 100
batch_size = 10000


# placeholders for a tensor that will be always fed.
X = tf.placeholder(tf.float32, shape=[None, 10])
Y = tf.placeholder(tf.float32, shape=[None, 1])

# dropout (keep_prob) rate  0.7 on training, but should be 1 for testing
keep_prob = tf.placeholder(tf.float32)

W1 = tf.get_variable("W1", shape=[10, 1], initializer=tf.contrib.layers.xavier_initializer())
b1 = tf.Variable(tf.random_normal([1]))	

hypothesis = tf.sigmoid(tf.matmul(X, W1) + b1)
cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1 - Y) * tf.log(1 - hypothesis))
train = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cost)

# Accuracy computation
# True if hypothesis>0.5 else False
predicted = tf.cast(hypothesis > 0.5, dtype=tf.float32)
accuracy = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), dtype=tf.float32))

saver = tf.train.Saver()
sess = tf.Session()
sess.run(tf.global_variables_initializer())
# train my model
for epoch in range(training_epochs):
	avg_cost = 0
	total_batch = int(len(xy) / batch_size)

	for i in range(total_batch):
		if i == total_batch -1:
			batch_xs = x_data[batch_size*i:]
			batch_ys = y_data[batch_size*i:]
		else:
			batch_xs = x_data[batch_size*i:batch_size*(i+1)]
			batch_ys = y_data[batch_size*i:batch_size*(i+1)]

		feed_dict = {X: batch_xs, Y: batch_ys, keep_prob: 0.7}
		c, _ = sess.run([cost, train], feed_dict=feed_dict)
		avg_cost += c / total_batch
	
	print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.9f}'.format(avg_cost))
save_path = saver.save(sess, "./sentence_tokenizer.ckpt")
print('Learning Finished!')
print("Accuracy:",sess.run(accuracy, feed_dict={X:x_test, Y:y_test, keep_prob: 1}))
h, c, a = sess.run([hypothesis, predicted, accuracy], feed_dict={X: x_test, Y: y_test})
print("\nHypothesis: ", h, "\nCorrect (Y): ", c, "\nAccuracy: ", a)
