#make dictionary for NELL relation

x = open("EKAW13Exp/NELLRelationDict.txt","w")

with open('Data/ListofRelations.txt') as a:
	seenRel=set()
	#i dimulai dari 63917 karena Dictionary Instance maximalnya 63916 ,
	#20467 so, start from 20468
	i=62866
	for line in a:
		row=line.split()
		if(row[0] not in seenRel):
			seenRel.add(row[0])
			x.write(row[0]+"\t"+str(i)+"\n")		
			i += 1
		
x.close()
