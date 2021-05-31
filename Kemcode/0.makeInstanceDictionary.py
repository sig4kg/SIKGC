#script ini untuk membuat dictionary NELL

output = open("EKAW13Exp/NELLInstanceDictionary.txt","w")

with open('EKAW13Exp/forPBRPropRel.txt') as a:

	seen=set()
	#seenRel = set()
	i = 0
	for line in a:
		row=line.split()
		if(row[0] not in seen):
			seen.add(row[0])
			output.write(row[0]+"\t"+str(i)+"\n")		
			i += 1
		
		#if(row[1] not in seenRel):
		#	seenRel.add(row[1])
		#	output.write(row[1]+"\t"+str(i)+"\n")		
		#	i += 1

		if(row[2] not in seen):
			seen.add(row[2])
			output.write(row[2]+"\t"+str(i)+"\n")
			i += 1

output.close

	

