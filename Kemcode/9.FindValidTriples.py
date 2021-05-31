import pdb
ori_all = open("EKAW13Exp/_newTriplesinInt.txt")
invalid = open("EKAW13Exp/NotValidWD.txt")
unknownWO = open("EKAW13Exp/UnknownWD.txt")

valid = open("EKAW13Exp/validTriples.txt","w")

dictInvalid={}
for iB,lineB in enumerate(invalid):
	kB = lineB
	vB = iB
	dictInvalid[kB]=vB

dictUnknown={}
for iC,lineC in enumerate(unknownWO):
	kC = lineC
	vC = iC
	dictUnknown[kC]=vC

for lineA in ori_all:		
	if (lineA not in dictUnknown)and(lineA not in dictInvalid):
		#pdb.set_trace()
		valid.write(lineA)

valid.close()


