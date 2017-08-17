w = open("herald_test_data.en.txt","w")

cnt = 0
for i in range(100):
	try:
		f = open("herald/eng/"+str(i)+".txt","r")
		tmp = f.readlines()
	except:
		continue
	
	if cnt >= 1000:
		break
	for j in range(len(tmp)):
		w.write(tmp[j])
		cnt+=1
	f.close()

w.close()

	
