import sys
import pickle
from nltk.classify import maxent
import argparse 
from datetime import datetime
import os 

class sentClassifier():
	def __init__(self, trainfile, testfile, lang, model):
		if trainfile is not None:
			self.trainfile = trainfile
		if testfile is not None:
			self.testfile = testfile 
		self.lang = lang 
		self.model = model

	def train_sentence(self):
		f=open(str(self.trainfile),"r")
		train_data=f.readlines()
		train=[]
		train_tmp=[]
		
		for i in range(len(train_data)):
			if i % 10000 == 0:
				print("Training Sentence:",i)
			train_split=train_data[i].split()
			if len(train_split) == 1:
				train_tmp.append(dict(a=train_split[0], b=" ", c=" "))
			elif len(train_split) == 2:
				train_tmp.append(dict(a=train_split[0], b=train_split[1], c=" "))
			else:
				train_tmp.append(dict(a=train_split[0], b=train_split[1], c=train_split[2]))
			train_tmp.append(train_split[len(train_split)-1])
			train_tuple=tuple(train_tmp)
			train_tmp=[]
			train.append(train_tuple)
		print("done")
		print("Training start!")
		encoding = maxent.TypedMaxentFeatureEncoding.train(train, count_cutoff=3, alwayson_features = True)
		classifier = maxent.MaxentClassifier.train(train, bernoulli=False, encoding=encoding, trace =0)
		save_file = open(str(self.model),"wb")
		pickle.dump(classifier, save_file)
		save_file.close()
		f.close()

	def test_sentence(self):

		read_file = open(str(self.model),"rb")
		classifier = pickle.load(read_file)
		read_file.close()

		for article in os.listdir(str(self.testfile)+"/"+str(self.lang)):

			f=open(str(self.testfile)+"/"+str(self.lang)+"/"+str(article),"r")
			outputfile=(str(self.testfile).split("."))[0]+"_output/"+str(self.lang)+"/"+str(article)
			out=open(str(outputfile),"w")
			test_data=f.readlines()
			test=[]

			for i in range(len(test_data)):
				test_split=test_data[i].split()
				if len(test_split) == 1:
					test.append(dict(a=test_split[0], b=" ", c=" "))
				elif len(test_split) == 2:
					test.append(dict(a=test_split[0], b= test_split[1], c=" "))
				else:
					test.append(dict(a=test_split[0], b= test_split[1], c= test_split[2]))

			result=classifier.classify_many(test)
		
			flag = 0
			previous = ""
			sentence = ""
			for i in range(len(result)):
				test_split=test_data[i].split()
				if result[i] == 'Y':
					flag = 0
					if len(test_split) == 2:
						sentence = sentence+" "+test_split[1]
						previous = test_split[1]
					else:
						sentence=sentence+" "+test_split[1]+" "+test_split[2]
						previous = test_split[2]
					out.write(sentence)
					out.write("\n")
					sentence=""
				else: 
					if flag == 0:
						flag = 1 
						if test_split[1] == previous:
							continue
						else:
							sentence = test_split[0]+" "+test_split[1]
					else:
						if len(sentence) == 0:
							sentence = test_split[1]
						else:
							sentence = sentence+" "+test_split[1]
			f.close()
			out.close()




	

	
if __name__ == '__main__':
	parser=argparse.ArgumentParser(description = 'sentence tokenizer.')
	parser.add_argument("--train", help = "training data file")
	parser.add_argument("--test", help = "test data file")
	parser.add_argument("--lang", help = "language of train or test file")
	parser.add_argument("--model", help = "classifier model")
	args = parser.parse_args()

	if (args.train is None and args.test is None) or args.lang is None or args.model is None:
		parser.print_help()
		sys.exit(1)
	
	a=sentClassifier(args.train, args.test, args.lang, args.model)

	if args.train is not None:
		start=datetime.now()
		a.train_sentence()
		end=datetime.now()
		print("time: ", end-start)
	
	if args.test is not None:
		a.test_sentence()
