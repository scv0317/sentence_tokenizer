import copy
import tensorflow as tf
import numpy as np
import sys
import argparse
import os
import re
from datetime import datetime


class training():
	default_options = {
	'dire': None,
	'suf': None,
	'lang': None,
	'mode': None,
	}

	def __init__(self, options):
		self.options = self.default_options.copy()
		self.options.update(options)

    # 학습 데이터 set을 만들기 위한 함수다.
    # csv 파일로 만들어 지며, trigram에 대한 feature set으로 데이터 set이 만들어진다. 
	def making_data(self):
		jobs =[]
		for source_document in [d for d in os.listdir(self.options['dire']) if d.endswith('.' + self.options['suf'])]:
			source_document = os.path.join(self.options['dire'], source_document)
			if not os.path.isfile(source_document):
				sys.stderr.write("ERROR: file {0} expected, but not found\n".format(f))
				exit()
			jobs.append(source_document)
		print("The number of train file is", len(jobs))
		print("Making data start!")
		train_file = open("train_data."+self.options['lang']+".csv", self.options['mode'])
		test_file = open("test_data."+self.options['lang']+".csv", self.options['mode'])
		i = 0 
		for source_document in jobs:
			i += 1
			source = open(source_document,"r")
			sentences = source.readlines()
			trigram_list = self.make_trigram(sentences)
			if self.options['lang'] == 'kor':
				feature_set_list = self.make_feature_set_kor(trigram_list)
			elif self.options['lang'] == 'eng':
				feature_set_list = self.make_feature_set_eng(trigram_list)
			for feature_set in feature_set_list:
				if i < 100:
					test_file.write(feature_set+'\n')
				else:
					train_file.write(feature_set+'\n')
			source.close()
		train_file.close()
		test_file.close()
		print("Finish making train data!")

    # 한 article에 있는 contents 들을 trigram으로 만든다.
	def make_trigram(self, sentences):
		trigram_list = []
		trigram = []	
		tmp_gram = []
		label = []
		for sentence in sentences:
			tmp_split = sentence.split()
			for i in range(len(tmp_split)):
				tmp_gram.append(tmp_split[i])
				if len(tmp_gram) == 3:
					temp = copy.deepcopy(tmp_gram)
					trigram.append(temp)
					del tmp_gram[0]
					if i == 0 :
						label.append(1)
					else:
						label.append(0)
		for i in range(len(trigram)):
			trigram_list.append(str(trigram[i][0])+" "+str(trigram[i][1])+" "+str(trigram[i][2])+" "+str(label[i]))
		return trigram_list

    # 영어 featrue set은 총 10가지의 feature로 이루어진다. 
	def make_feature_set_eng(self, trigram_list):
		feature_set_list = []
		feature = []
		feature_set = [0 for i in range(10)]	
		NP = [ 'Who', 'Which', 'That', 'The', 'What', 'How' ]
		for trigram in trigram_list:
			tmp_split = trigram.split()
			feature_set = [0 for i in range(10)]	
			# feature 1
			if tmp_split[0][0].islower() and tmp_split[2][0].isupper():
				feature_set[0] = 1 
			# feature 2
			if tmp_split[0].isupper():
				feature_set[1] = 1
			# feature 3
			if tmp_split[1][-1] == ':' or tmp_split[1][-2:] == '--' or tmp_split[1][-1] == '…':
				feature_set[2] = 1
			# feature 4
			if tmp_split[2] == '$':
				feature_set[3] = 1
			# feature 5
			if tmp_split[2].replace('.','').isnumeric():
				feature_set[4] = 1
			# feature 6
			if tmp_split[0].find('.') != -1:
				if tmp_split[2].replace('.','').isalpha():
					feature_set[5] = 1
			# feature 7
			if ( tmp_split[1][-1] == '.' or tmp_split[1][-1] == '?' or tmp_split[1][-1] =='!' ) and ( tmp_split[2] == '--' or tmp_split[2][0] == '\"' or tmp_split[2][0] == '“' ):
				feature_set[6] = 1
			# feature 8 
			if ( tmp_split[1][-1] == '.' or tmp_split[1][-1] =='?' or tmp_split[1][-1] =='!' ) and ( tmp_split[2][0] != '\"' and tmp_split[2][0] !='“'):
				feature_set[7] = 1
			# feature 9 
			if len(tmp_split[1]) >= 2:
				if ( tmp_split[1][-2] == '.' or tmp_split[1][-2] =='?' or tmp_split[1][-2] =='!' ) and ( tmp_split[1][-1] =='\'' or tmp_split[1][-1] == '’' or tmp_split[1][-1] == '\"' or tmp_split[1][-1] == "”" ) and ( tmp_split[2][0] =='\"' or tmp_split[2][0] == '“' or tmp_split[2][0].isupper()):
					feature_set[8] = 1
			if tmp_split[2] in NP:
				feature_set[9] = 1
	
			tmp_feature = copy.deepcopy(feature_set)
			feature.append(tmp_feature)
	
		for i in range(len(feature)):
			feature_tmp=''
			for j in range(len(feature[i])):
				if j == 9:
					try:
						if trigram_list[i][-1] == '1':
							feature_tmp=feature_tmp+str(feature[i][j])+",1"
						else:
							feature_tmp=feature_tmp+str(feature[i][j])+",0"
					except:
						print(i)
				else:
					feature_tmp=feature_tmp+str(feature[i][j])+","

			feature_set_list.append(feature_tmp)

		return feature_set_list

    # 한글에 대한 feature는 총 3가지로 이루어진다. 
	def make_feature_set_kor(self, trigram_list):
		feature_set_list = []
		feature = []
		punct = ['.','?','!']
		quotes = ['\"','\'','“','‘']
		parenthese = ['(','[','{',')',']','}']
		feature_set = [0 for i in range(3)]
		for trigram in trigram_list:
			tmp_split = trigram.split()
			feature_set = [0 for i in range(3)]
			if tmp_split[1][-1] in punct:
				feature_set[0] = 1
			if tmp_split[2][0] in quotes:
				feature_set[1] = 1
			if tmp_split[1][-1] in parenthese:
				feature_set[2] = 1

			tmp_feature = copy.deepcopy(feature_set)
			feature.append(tmp_feature)

		for i in range(len(feature)):
			feature_tmp = ''
			for j in range(len(feature[i])):
				if j == 2:
					try:
						if trigram_list[i][-1] == '1':
							feature_tmp = feature_tmp + str(feature[i][j]) + ",1"
						else:
							feature_tmp = feature_tmp + str(feature[i][j]) + ",0"
					except:
						print(i)
				else:
					feature_tmp = feature_tmp + str(feature[i][j]) + ","
			feature_set_list.append(feature_tmp)
		return feature_set_list
			
    # 모델을 학습시킨다. 
	def training_data(self):
		tf.set_random_seed(777)
		xy = np.loadtxt("train_data."+self.options['lang']+".csv",delimiter = ',', dtype = np.float32)
		test = np.loadtxt("test_data."+self.options['lang']+".csv",delimiter = ',', dtype = np.float32)

		x_data = xy[:,0:-1]
		y_data = xy[:,[-1]]
		x_test = test[:,0:-1]
		y_test = test[:,[-1]]
		print(x_data.shape, y_data.shape)

		learning_rate = 0.07
		training_epochs = 100
		batch_size = 10000
		
		if self.options['lang'] == 'eng':
			X = tf.placeholder(tf.float32, shape = [None, 10])
		elif self.options['lang'] =='kor':
			X = tf.placeholder(tf.float32, shape = [None, 3])

		Y = tf.placeholder(tf.float32, shape = [None, 1])
		keep_prob = tf.placeholder(tf.float32)
		if self.options['lang'] == 'eng':
			W = tf.get_variable("W",shape = [10, 1], initializer = tf.contrib.layers.xavier_initializer())
		elif self.options['lang'] == 'kor':
			W = tf.get_variable("W",shape = [3, 1], initializer = tf.contrib.layers.xavier_initializer())
		B = tf.Variable(tf.random_normal([1]))

		hypothesis = tf.sigmoid(tf.matmul(X, W) + B)
		cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1 - Y) * tf.log(1 - hypothesis))
		train = tf.train.GradientDescentOptimizer(learning_rate = learning_rate).minimize(cost)
		predicted = tf.cast(hypothesis > 0.5, dtype = tf.float32)
		accuracy = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), dtype = tf.float32))

		saver = tf.train.Saver()
		sess = tf.Session()
		sess.run(tf.global_variables_initializer())
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
				c, _ = sess.run([cost, train], feed_dict = feed_dict)
				avg_cost += c / total_batch
			print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.9}'.format(avg_cost))
		save_path = saver.save(sess, "./sentence_tokenizer."+self.lang+".ckpt")
		print('Learning Finished!')
		h, c = sess.run([hypothesis, predicted], feed_dict = {X: x_test, Y: y_test})
		label = 0 
		machine = 0 
		for i in range(len(y_test)):
			if y_test[i] == [ 1.]:
				label += 1
				if c[i] == [ 1.]:
					machine += 1
		print("label:", label, "machine:", machine, "recall:", machine/label)
		machine = 0 
		label = 0 
		for i in range(len(c)):
			if c[i] == [ 1.]:
				machine += 1
				if y_test[i] == [ 1.]:
					label += 1
		print("machine:", machine, "label:", label, "precision:", label/machine)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'making and training data.')
	parser.add_argument("--dire", help = 'Training data directory.')
	parser.add_argument("--suf", help = 'Training data suffix.')
	parser.add_argument("--lang", help = 'language of training data')
	parser.add_argument("--train", help = 'Train data or make data not.(y/n)')
	parser.add_argument("--mode", help = 'w or a')
	args = parser.parse_args()

	options = {}
		
	if args.train is None:
		parser.print_help()
		sys.exit()

	if str(args.train).upper() == 'Y':
		if args.lang is None:
			parser.print_help()
			sys.exit()
		options['lang'] = args.lang 
		train = training(options)
		start = datetime.now()
		train.training_data()
		end = datetime.now()
		print("Training time: {}".format(end - start))

	elif str(args.train).upper() == 'N':
		if args.dire is None or args.suf is None or args.mode is None:
			parser.print_help()
			sys.exit()
		options['dire'] = args.dire
		options['suf'] = args.suf
		options['mode'] = args.mode
		train = training(options)
		start = datetime.now()
		train.making_data()
		end = datetime.now()
		print("Making time: {}".format(end - start)) 	

	else:
		parser.print_help()
		sys.exit()

