import copy




def sum_train_data(start, end):

	w = open("wiki_sentence_data.en.txt","w")
	for i in range(start, end):
		try:
			f = open("../corpus/wiki/eng/"+str(i)+".txt","r")
		except:
			continue 
		tmp = f.readlines()
		for j in range(len(tmp)):
			w.write(tmp[j])

		f.close()

	w.close()
	
def make_three_gram():
	f = open("wiki_sentence_data.en.txt","r")
	w = open("wiki_three_gram.en.txt","w")

	tmp = f.readlines()
	three_gram = []	
	tmp_gram = []
	label = []
	for i in range(len(tmp)):
		tmp_split = tmp[i].split()
		for j in range(len(tmp_split)):
			tmp_gram.append(tmp_split[j])
			if len(tmp_gram) == 3:
				ttt = copy.deepcopy(tmp_gram)
				three_gram.append(ttt)
				del tmp_gram[0]
				if j == 0 :
					label.append(1)
				else:
					label.append(0)
				

	for i in range(len(three_gram)):
		w.write(str(three_gram[i][0])+" "+str(three_gram[i][1])+" "+str(three_gram[i][2])+" "+str(label[i]))
		w.write("\n")
	
	f.close()
	w.close()

def make_feature_set():
	f = open("wiki_three_gram.en.txt","r")
	w = open("wiki_feature_set.en.csv","w")
	feature = []
	feature_set = [0 for i in range(10)]	
	tmp = f.readlines() 
	NP = [ 'Who', 'Which', 'That', 'The', 'What', 'How' ]
	for i in range(len(tmp)):#len(tmp)
		tmp_split = tmp[i].split()
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
					if tmp[i][-2] == '1':
						feature_tmp=feature_tmp+str(feature[i][j])+",1"
					else:
						feature_tmp=feature_tmp+str(feature[i][j])+",0"
				except:
					print(i)
			else:
				feature_tmp=feature_tmp+str(feature[i][j])+","


		w.write(str(feature_tmp))
		w.write('\n')
	f.close()
	w.close()

sum_train_data(0, 50)
print("sum_train_data finish")
make_three_gram()
print("make_three_gram finish")
make_feature_set()
print("make_feature_set finish")


