import sys
import argparse
import os 

class trigram():
	def __init__(self, trainfile, testfile, lang):
		self.trainfile = trainfile
		self.testfile = testfile
		self.lang = lang
		if trainfile is not None:
			self.train_start=101
			self.train_end=len(os.listdir(str(trainfile)+"/"+str(lang)))
		if testfile is not None:
			self.test_start=0
			self.test_end=100
	
	def train_trigram(self):
		trigram_list=[]
		for i in range(self.train_start, self.train_end):
			if i % 10000 == 0:
				print("The number of training sentence is : ",i)
			try:
				article = open(str(self.trainfile)+"/"+str(self.lang)+"/"+str(i)+".txt","r")
				sentences = article.readlines()
			except:
				continue
			
			for i in range(len(sentences)):
				token = sentences[i].split()
				for j in range(len(token)):
					if len(token) == 1:
						label= ' Y'
						features = token[j]
						trigram_list.append([features, label])
					elif len(token) == 2:
						label = ' Y'
						features = token[j]+" "+token[j+1]
						trigram_list.append([features, label])
						break
					else:
						if j == len(token) - 3:
							label = ' Y' 
							features = token[j]+" "+token[j+1]+" "+token[j+2]
							trigram_list.append([features, label])
							break
						else:
							label = ' N'
							features = token[j]+" "+token[j+1]+" "+ token[j+2]
							trigram_list.append([features, label])
		print("done")
		train_data=open("train_test."+str(self.lang)+".txt","w")
		print("The number of trigram for train is: ", len(trigram_list))
		for i in range(len(trigram_list)):
			train_data.write(trigram_list[i][0])
			train_data.write(trigram_list[i][1])
			train_data.write("\n")
		print("done")

		article.close()
		train_data.close()


	def test_trigram(self):
		for i in range(self.test_start, self.test_end):
			test_trigram=[]
			try:
				article = open(str(self.testfile)+"/"+str(self.lang)+"/"+str(i)+".txt","r")
				sentences = article.readlines()
			except:
				continue
			for j in range(len(sentences)):
				token=sentences[j].split()
				for k in range(len(token)):
					if len(token) == 1:
						features = token[k]
						test_trigram.append(features)
						break
					elif len(token) == 2:
						features = token[k]+" "+token[k+1]
						test_trigram.append(features)
						break
					else:
						if k == len(token) - 3:
							features = token[k]+" "+token[k+1]+" "+token[k+2]
							test_trigram.append(features)
							break
						else:
							features = token[k]+" "+token[k+1]+" "+token[k+2]
							test_trigram.append(features)

			test_data = open(str(self.testfile)+"_test/"+str(self.lang)+"/"+str(i)+".txt","w")
			print("The number of trigram for test is :", len(test_trigram))
			for j in range(len(test_trigram)):
				test_data.write(test_trigram[j])
				test_data.write("\n")
			print(str(i)+" article is done")
			
			test_data.close()
			article.close()
			 
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Make trigram.')
	parser.add_argument("--train", help = "original train sentence file")
	parser.add_argument("--test", help = "original test sentence file")
	parser.add_argument("--lang", help = "language of train or test file") 
	args = parser.parse_args()

	if (args.train is None and args.test is None) or args.lang is None:
		parser.print_help()
		sys.exit(1)
	
	a = trigram(args.train, args.test, args.lang)

	if args.train is not None:
		a.train_trigram()

	if args.test is not None:
		a.test_trigram()





