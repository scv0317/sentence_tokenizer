import os
import sys
import argparse
import copy
import re
from nltk import sent_tokenize

class sentence_tokenizer():

	def __init__(self, kor_dir, kor_suffix, eng_dir, eng_suffix):
		self.kor_dir = kor_dir
		self.kor_suffix = kor_suffix
		self.eng_dir = eng_dir
		self.eng_suffix = eng_suffix 

	# 디렉토리에 있는 모든 한글 Source에 대해서 문장 분리를 한다.
	# 분리된 문장은 'sentence_tokenizer/' 하위 디렉토리에 Source와 동일한 경로의 파일에 쓰여진다. 	
	def korean_sentence(self):
		jobs = []
		for source_document in [d for d in os.listdir(self.kor_dir) if d.endswith('.' + self.kor_suffix)]:
			source_document = os.path.join(self.kor_dir, source_document)
			if not os.path.isfile(source_document):
				sys.stderr.write("ERROR: File {0} expected, but not found\n".format(f))
				exit()
			jobs.append(source_document)
		print("The number of Korean source is", len(jobs))
		print("Korean sentence tokenizer start!")
		i = 0
		for source_document in jobs:
			source = open(source_document, "r")
			target = open("sentence_tokenizer/"+source_document,'w')
			source_list = source.readlines()
			kor_string =''
			for kor in source_list:
				kor_string = kor_string+str(kor)
			# 헤드라인, 이미 개행된 문장의 정보, 또는 문단의 정보는 살리고, 모든 데이터를 한 String으로 만들어서 문장별로 분리한다. 
			kor_string = kor_string.replace('\n', '**divide**')
			korean_sentence_list = self.sentence_tokenizer_kor(kor_string)
			for sentence in korean_sentence_list:
				if len(sentence) >= 3:
					target.write(sentence)
			source.close()
			target.close()
			i += 1
			if i % 1000 == 0:
				print(str(i),"korean source complete...")

	def sentence_tokenizer_kor(self, kor_string):
		# Rule base 기반으로 한글을 문장별로 분리할때 아래와 같은 종결어미와 구두점이 쓰인다. (경험적으로 구했다.)
		endword = ['가','나','다','라','까','지','자','요','죠','네','오','야','어','해','든','게','돼','아',
			   '봐','데','래','대','군','론','소','렴','걸','와','마','줘','고','것','들','랴','\'','\"','’','”',')',']','}']
		punct = ['．','.','?','!','…']
		temp=""
		sentence_list = []
		double = 0 
		single = 0
		quotes_error = 0 
		quotes_error_sentence = []
		for i in range(len(kor_string)):
			if kor_string[i] == '\n':
				continue 
			if i == 0:
				previous = 'N'
			else:
				previous = kor_string[i-1]
			# double quotes나 single quotes안에 존재하는 문장들은 인용구로써 일반적으로 개행해서는 안되기 때문에 아래와 같은 flag를 사용한다.  
			if (kor_string[i] == '\"' or kor_string[i] == '“') and double == 0:
				double = 1
			elif (kor_string[i] =='\"' or kor_string[i] == '”') and double == 1:
				double = 0
			if (kor_string[i] == '\'' or kor_string[i] == '‘') and single == 0:
				single = 1
			elif (kor_string[i] == '\'' or kor_string[i] == '’') and single == 1:
				single = 0
			# 아래의 과정은 종결어미, 구두점, quotes flag와 기타정보를 활용하여 한글을 문장별로 분리한다. 		
			# 첫번째 if문은 quotes가 문법적 오류로 인해서 제대로 닫히지 않았을 경우를 대비하기 위함이다. quotes안의 문장의 갯수만큼 quotes_error가 증가하게 되고, 
			# 10개(default 값)의 문장이 나왔음에도 닫히지 않는다면 오른쪽 quotes가 없는 문법적 오류로 간주하고 모든 문장들을 다 분리시킨다. 
			if kor_string[i] in punct and previous in endword and (double == 1 or single == 1):
				quotes_error += 1 
			if kor_string[i] in punct and previous in endword and double == 0 and single == 0:
				temp, sentence_list, quotes_error, quotes_error_sentence = self.complete_kor_sentence(temp, sentence_list, kor_string[i])
			elif kor_string[i] in punct and previous == ')' and kor_string[i-2] in endword and double == 0 and single == 0:
				temp, sentence_list, quotes_error, quotes_error_sentence = self.complete_kor_sentence(temp, sentence_list, kor_string[i])
			elif kor_string[i] in punct and previous in endword and quotes_error != 0:
				temp = temp + kor_string[i] 
				if quotes_error == 1:
					quotes_error_sentence.append(temp + '\n')
				else:
					quotes_error_sentence.append(temp.replace(quotes_temp,'') + '\n')
				quotes_temp = copy.deepcopy(temp)
				if quotes_error > 10: 
					for sentence in quotes_error_sentence:
						sentence_list.append(sentence)
					double = 0
					single = 0
					quotes_error = 0
					quotes_error_sentence = []
					quotes_temp = '' 
					temp = ''
			else:
				temp = temp + kor_string[i] 
		# 문장별 분리 이후 후처리로 이미 존재하는 헤드라인, 문장의 구분, 문단의 구분 정보는 살리고, 각 문장의 맨앞에 불필요하게 남아있는 공백이나 개행은 제거한다. 
		for i in range(len(sentence_list)):
			index = 0
			sentence_list[i] = sentence_list[i].replace('**divide**','\n')
			sentence_list[i] = sentence_list[i].replace('\n \n','\n')
			for j in range(len(sentence_list[i])):
				if sentence_list[i][j] == ' ' or sentence_list[i][j] == '\n' or sentence_list[i][j] == '.':
					index += 1
				else:
					break
			sentence_list[i] = sentence_list[i][index:len(sentence_list[i])]
			double_new_line = 0			
			while double_new_line != -1: 
				double_new_line = sentence_list[i].find('\n\n')
				sentence_list[i] = sentence_list[i].replace('\n\n','\n')
		return sentence_list 

	# 문장을 완성시키고 다음 문장을 만드는데 필요한 변수를 초기화한다.  
	def complete_kor_sentence(self, temp, sentence_list,  word):
		temp = temp + word + '\n'
		sentence_list.append(temp)
		temp = ''
		quotes_error = 0 
		quotes_error_sentence = []
		return temp, sentence_list, quotes_error, quotes_error_sentence  

	def english_sentence(self):
		jobs = []
		for source_document in [d for d in os.listdir(self.eng_dir) if d.endswith('.' + self.eng_suffix)]:
			source_document = os.path.join(self.eng_dir, source_document)
			if not os.path.isfile(source_document):
				sys.stderr.write("ERROR: File {0} expected, but not found\n".format(f))
				exit()
			jobs.append(source_document)
		print("===========================================")
		print("\nThe number of English source is", len(jobs))
		print("English sentence tokenizer start!")
		i = 0 
		for source_document in jobs:
			source = open(source_document, "r")
			target = open("sentence_tokenizer/"+source_document,'w')
			source_list = source.readlines()
			english_sentence_list = self.sentence_tokenizer_eng(source_list)
			for sentence in english_sentence_list:
				if len(sentence) >= 3:
					target.write(sentence)
			source.close()
			target.close()
			i += 1
			if i % 1000 == 0:
				print(str(i),"English source complete...")

	def sentence_tokenizer_eng(self, source_list):
		# Month에 대한 약어와 기타 확인된 약어를 전처리하여 약어에서 개행되지 않도록 하기 위함이다. 
		abbreviation = ['Jan.','Feb.','Mar.','April.','May.','Jun.','July.','Jul.','Aug.','Sep.','Oct.','Nov.','Dec.','a.k.a','No.']
		punct = ['．','.','!','?','…']
		left = ['\"','“','＂','(']
		right = ['\"','”','＂',')']
		english_sentence_list = []
		for source in source_list:
			flag = 0 
			for ab in abbreviation:
				if ab in source:
					source = source.replace(ab, ab[:-1]+'#ab1#')
			source = source.replace("\u3000\n","\n")
			source = source.replace(" \n","\n")
			source = source.replace(".” ",".”\n")
			source = source.replace(".\" ",".\"\n")
			# 대문자로 구성되어 있는 약어들을 전처리하기 위함이다. 
			p = re.compile("[A-Z]\.[ ]?")
			abbreviation_upper = p.findall(source)
			ab_idx = 0
			for ab in abbreviation_upper:
				source = source.replace(ab, "#ab2-"+str(ab_idx)+"#")
				ab_idx += 1 
			question_mark_idx = 0 
			while True:
				question_mark_idx = source.find("?” ", question_mark_idx+1)
				if question_mark_idx == -1:
					break
				if ord(source[question_mark_idx + 3]) >= 65 and ord(source[question_mark_idx + 3]) <= 90:
					source = source[:question_mark_idx + 2] + '\n' + source[question_mark_idx + 3:]
			for i in range(len(source)):
				if flag == 1 and source[i] in punct and i+1 < len(source):
					if source[i+1] not in right:
						if source[i] == '?':
							source = source[:i] + "#qm#" + source[i+1:]
						elif source[i] == '.':
							source = source[:i] + "#pe#" + source[i+1:]
						elif source[i] == '!':
							source = source[:i] + "#em#" + source[i+1:]
				if flag == 1 and source[i] == '(':
					flag = 2
				elif (flag == 2 and source[i] == ')') or (flag == 0 and source[i] in left ):
					flag = 1
				elif flag == 1 and source[i] in right:
					flag = 0 
			english_sentences = sent_tokenize(source)
			for i in range(len(english_sentences)):
				ab_idx = 0
				for ab in abbreviation_upper:
					english_sentences[i] = english_sentences[i].replace("#ab2-"+str(ab_idx)+"#",ab)
					ab_idx += 1 
				for ab in abbreviation:
					english_sentences[i] = english_sentences[i].replace(ab[:-1]+'#ab1#',ab)
				english_sentences[i] = english_sentences[i].replace('#qm#','?')
				english_sentences[i] = english_sentences[i].replace('#pe#','.')
				english_sentences[i] = english_sentences[i].replace('#em#','!')
				english_sentence_tmp = copy.deepcopy(english_sentences[i])
				english_sentence_list.append(english_sentence_tmp+'\n')
		for i in range(len(english_sentence_list)):
			double_new_line = 0 
			while double_new_line != -1:
				double_new_line = english_sentence_list[i].find('\n\n')
				english_sentence_list[i] = english_sentence_list[i].replace('\n\n','\n')
		return english_sentence_list 


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'sentence tokenizer.')
	parser.add_argument("--kordir", help = "Korean Source Directory.")
	parser.add_argument("--kor", help = "Korean Source Suffix.")
	parser.add_argument("--engdir", help = "English Source Directory.")
	parser.add_argument("--eng", help = "English Source Suffix.")
	args = parser.parse_args()
    

	if (args.kordir is None or args.kor is None) and (args.engdir is None or args.eng is None):
		parser.print_help()
		sys.exit(1)


	sent = sentence_tokenizer(args.kordir, args.kor, args.engdir, args.eng)
	if args.kor is not None:
		sent.korean_sentence()
		print("korean sentence tokenizing is done!")
	if args.eng is not None:
		sent.english_sentence()
		print("english sentence tokenizing is done!")

	
