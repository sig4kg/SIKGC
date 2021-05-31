a = open("_Ev6.4RuleFlow2/2ndIteration/2ndPBRChecking/newTriplescheck.txt")
b = open("_Ev6.4RuleFlow2/2ndIteration/2ndPBRChecking/newTriplescheckFix.txt","w")

for line in a:
	row = line.split()
	b.write(row[0]+"\t"+row[2]+"\t"+row[1]+"\n")

b.close()