#make dictionary for NELL classes

x = open("EKAW13Exp/NELLClassDict.txt","w")

with open('Data/ListofClasses.txt') as a:
	seenClass=set()
	#i dimulai dari 64811 karena Dictionary relation maximalnya 64810
	#21361 so start from 21361
	i=63760
	for line in a:
		row=line.split()
		if(row[0] not in seenClass):
			seenClass.add(row[0])
			x.write(row[0]+"\t"+str(i)+"\n")		
			i += 1
		
x.close()
