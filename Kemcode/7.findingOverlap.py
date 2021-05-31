a=open("EKAW13Exp/NotValidWD.txt")
b=open("EKAW13Exp/UnknownWD.txt")

c = open("EKAW13Exp/OverlapTripleTemp.txt","w")

dictB = {}
for i2,line2 in enumerate(b):
	k2 = line2
	v2 = i2
	dictB[k2]=v2

for lineA in a:
	if lineA in dictB:
		c.write(lineA)

c.close()
