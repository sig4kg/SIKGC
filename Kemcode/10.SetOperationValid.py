from sets import Set

#ori_all = set(open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/TripletsClassification/Data/_NELLTCinInteger.txt"))
ori_all = set(open("IC3Flow2-Ite1/_dataIte1InInt.txt"))
invalid = set(open("IC3Flow2-Ite1/NotValidWD.txt"))
unknownWO = set(open("IC3Flow2-Ite1/unknownWithoutOverlap.txt"))

c = open("IC3Flow2-Ite1/validTriples.txt","w")

validTriple = ori_all-invalid-unknownWO

for line in validTriple :
	c.write(line)

c.close()


