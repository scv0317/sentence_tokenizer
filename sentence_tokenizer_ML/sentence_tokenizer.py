import tensorflow as tf
import numpy as np 
import sys 
import argparse
import os 
import copy
import re


class sentence_tokenizer():
	def __init__(self, dire, suf, model, lang):
		self.dire = dire
		self.suf = suf
		self.model = model 
		self.lang = lang
		self.abbreviation = ['Jan.','Feb.','Mar.','April.','May.','Jun.','Jul.','Aug.','Sep.','Oct.','Nov.','Dec.','a.k.a','No.','Mr.','Ms.']
	def main(self):
		jobs = []
		for source_document in [d for d in os.listdir(self.dire) if d.endswith('.' + self.suf)]:
			source_document = os.path.join(self.dire, source_document)
			if not os.path.isfile(source_document):
				sys.stderr.write("ERROR: file {0} expected, but not found\n".format(f))
				exit()
			jobs.append(source_document)
		print("The number of source is", len(jobs))
		if self.lang == 'eng':
			print("English sentence tokenizer start!")
		elif self.lang == 'kor':
			print("Korean sentence tokenizer start!")
		tf.set_random_seed(777)
		if self.lang == 'eng':
			X = tf.placeholder(tf.float32, shape = [None, 10])
		elif self.lang == 'kor':
			X = tf.placeholder(tf.float32, shape = [None, 3])
		Y = tf.placeholder(tf.float32, shape = [None, 1])
		if self.lang == 'eng':
			W = tf.get_variable("W", shape = [10, 1], initializer = tf.contrib.layers.xavier_initializer())
		elif self.lang == 'kor':
			W = tf.get_variable("W", shape = [3, 1], initializer = tf.contrib.layers.xavier_initializer())
		B = tf.Variable(tf.zeros([1]))
		hypothesis = tf.sigmoid(tf.matmul(X,W) + B)
		saver = tf.train.Saver()
		predicted = tf.cast(hypothesis > 0.5 , dtype = tf.float32)
		with tf.Session() as sess:
			saver.restore(sess, self.model)
			i = 0 
			for source_document in jobs:
				source = open(source_document, "r")
				target = open("sentence_tokenizer/"+source_document,'w')
				source_list = source.readlines()
				source_trigram = self.make_trigram(source_list)
				if len(source_trigram) < 5:
					continue
				if self.lang == 'eng':
					source_feature_set = self.make_english_feature_set(source_trigram)
				elif self.lang == 'kor':
					source_feature_set = self.make_korean_feature_set(source_trigram)
				h, correct = sess.run([hypothesis, predicted], feed_dict = {X: source_feature_set })
				source_sentence = self.make_sentence(correct, source_trigram)
				for sentence in source_sentence:
					if len(sentence) >= 3:
						target.write(sentence)
				source.close()
				target.close()
				i += 1
				if i % 1000 == 0:
					print(str(i), "source complete...")
			
	def make_trigram(self, source_list):
		source_trigram = []
		trigram = []
		tmp_gram = []
		for i in range(len(source_list)):
			sentence_split = source_list[i].split()
			for j in range(len(sentence_split)):
				tmp_gram.append(sentence_split[j])
				if len(tmp_gram) == 3:
					tmp = copy.deepcopy(tmp_gram)
					trigram.append(tmp)
					del tmp_gram[0]
		for i in range(len(trigram)):
			source_trigram.append(str(trigram[i][0])+" "+str(trigram[i][1])+" "+str(trigram[i][2]))
		return source_trigram

	def make_english_feature_set(self, source_trigram):
		source_feature_set = []
		feature_set = [0 for i in range(10)]
		NP = [ 'Who', 'Which', 'That', 'The', 'What', 'How' ]
		for i in range(len(source_trigram)):
			
			trigram_temp = copy.deepcopy(source_trigram[i])
			trigram_split = trigram_temp.split()
			for i in range(len(trigram_split)):
				for ab in self.abbreviation:
					if ab in trigram_split[i]:
						trigram_split[i] = trigram_split[i].replace(ab, 'Ab1')
				p = re.compile("[A-Z]\.[ ]?")
				abbreviation_upper = p.findall(trigram_split[i])
				for ab in abbreviation_upper:
					trigram_split[i] = trigram_split[i].replace(ab, 'AB2')
			feature_set = [0 for i in range(10)]
			# feature 1
			if trigram_split[0][0].islower() and trigram_split[2][0].isupper():
				feature_set[0] = 1 
			# feature 2
			if trigram_split[0].isupper():
				feature_set[1] = 1
			# feature 3
			if trigram_split[1][-1] == ':' or trigram_split[1][-2:] == '--' or trigram_split[1][-1] == '…':
				feature_set[2] = 1
			# feature 4
			if trigram_split[2] == '$':
				feature_set[3] = 1
			# feature 5
			if trigram_split[2].replace('.','').isnumeric():
				feature_set[4] = 1
			# feature 6
			if trigram_split[0].find('.')!= -1:
				if trigram_split[2].replace('.','').isalpha():
					feature_set[5] = 1
			# feature 7 
			if ( trigram_split[1][-1] == '.' or trigram_split[1][-1] == '?' or trigram_split[1][-1] =='!' ) and ( trigram_split[2] == '--' or trigram_split[2][0] == '\"' or trigram_split[2][0] == '“'):
				feature_set[6] = 1
			# feature 8
			if ( trigram_split[1][-1] == '.' or trigram_split[1][-1] == '?' or trigram_split[1][-1] == '!' ) and ( trigram_split[2][0] !='\"' and trigram_split[2][0] != '“'):
				feature_set[7] = 1
			# feature 9
			if len(trigram_split[1]) >= 2:
				if ( trigram_split[1][-2] == '.' or trigram_split[1][-2] == '?' or trigram_split[1][-2] == '!') and ( trigram_split[1][-1] == '\'' or trigram_split[1][-1] == '’' or trigram_split[1][-1] == '\"' or trigram_split[1][-1] =='”') and (trigram_split[2][0] == '\"' or trigram_split[2][0] == '“' or trigram_split[2][0].isupper()):
					feature_set[8] = 1
			# feature 10
			if trigram_split[2] in NP:
				feature_set[9] = 1
			tmp_feature = copy.deepcopy(feature_set)
			source_feature_set.append(tmp_feature)
		return source_feature_set  

	def make_korean_feature_set(self, source_trigram):
		source_feature_set =[]
		feature_set = [0 for i in range(3)]
		punct = ['.','?','!']
		quotes = ['\'','\"','“','‘']
		parenthese = ['(','[','{',')',']','}']
		for trigram in source_trigram:
			tmp_split = trigram.split()
			feature_set = [0 for i in range(3)]
			if tmp_split[1][-1] in punct:
				feature_set[0] = 1
			if tmp_split[2][0] in quotes:
				feature_set[1] = 1
			if tmp_split[1][-1] in parenthese:
				feature_set[2] = 1
			tmp_feature = copy.deepcopy(feature_set)
			source_feature_set.append(tmp_feature)
		return source_feature_set
	
	def make_sentence(self, correct, source_trigram):
		source_sentence = [] 
		sentence_tmp =''
		for i in range(len(correct)):
			trigram_split = source_trigram[i].split()
			if i == 0:
				sentence_tmp = trigram_split[0] + ' ' + trigram_split[1]+ ' '
			else:
				sentence_tmp = sentence_tmp + trigram_split[1] + ' '
				if correct[i] == 1:
					temp = copy.deepcopy(sentence_tmp)
					source_sentence.append(temp+'\n')
					sentence_tmp = '' 
		return source_sentence
			
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Sentence totenizer.')
	parser.add_argument("--dire", help = 'Source directory.')
	parser.add_argument("--suf", help = 'Source file suffix.')
	parser.add_argument("--model", help = 'Sentence tokenizer model.')
	parser.add_argument("--lang", help = 'Sentence tokenizer language.')
	args = parser.parse_args()

	if args.dire is None or args.suf is None or args.model is None or args.lang is None:
		parser.print_help()
		sys.exit()
	
	sent = sentence_tokenizer(args.dire, args.suf, args.model, args.lang)
	sent.main()

