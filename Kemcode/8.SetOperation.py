from sets import Set

unknownWD = set(open("EKAW13Exp/UnknownWD.txt"))
overlap = set(open("EKAW13Exp/OverlapTripleTemp.txt"))

c = open("EKAW13Exp/unknownWithoutOverlap.txt","w")

unknownWithoutOverlap = unknownWD-overlap 

for line in unknownWithoutOverlap:
	c.write(line)

c.close()


