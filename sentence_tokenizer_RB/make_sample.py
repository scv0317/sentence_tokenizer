import random 
import os
import sys
import argparse

def make_sample(directory, suffix, size):
	jobs = []
	for source_document in [d for d in os.listdir(directory) if d.endswith('.' + suffix)]:
		source_document = os.path.join(directory, source_document)
		if not os.path.isfile(source_document):
			sys.stderr.write("ERROR: File {0} expected, but not found\n".format(f))
			exit()
		jobs.append(source_document)
	print("The number of source is", len(jobs))
	print("Sentence sampling...")
	i = -1 
	document_interval = int(len(jobs) / int(size))
	sample = open(directory+"/sample.txt","w")
	tmp = []
	for source_document in jobs:
		i += 1
		if i % document_interval != 0:
			continue
		source = open(source_document,"r")
		source_list = source.readlines()
		try:
			idx = random.randrange(0, len(source_list))
		except:
			source.close()
			continue
		tmp.append(source_list[idx])
		sample.write(source_list[idx])
		source.close()
	sample.close()	
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'sentence sampling.')
	parser.add_argument("--dire", help = "Sentence source directory.")
	parser.add_argument("--suf", help = "Sentence source suffix.")
	parser.add_argument("--size", help = "Sentence sample size.")
	args = parser.parse_args()

	if args.dire is None or args.suf is None:
		parser.print_help()
		sys.exit(1)

	make_sample(args.dire, args.suf, args.size)

