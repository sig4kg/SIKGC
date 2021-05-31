#script for linking instance and class
import pdb
a = open("EKAW13Exp/NELLInstanceDictionary.txt")
b = open("EKAW13Exp/NELLClassDict.txt")
c = open("EKAW13Exp/Instance_Class.txt","w")

#format output:
#kolom pertama : ID instance misalnya 78 
#kolom kedua : ID class misalnya 1000
classDict = {}
for lineB in b:
	rowB = lineB.split()
	#kolom 1 adalah string Class NELL 
	#kolom 2 adalah integer
	k = rowB[0] 
	v = rowB[1]
	classDict[k]=v

values = ""
for lineA in a:
	#a punya 2 kolom
	#class:instance	IDnya
	rowA = lineA.split()
	classLabel = rowA[0].split("_")
	#pdb.set_trace()
	classLabelx = "http://ste-lod-crew.fr/nell/ontology/"+''.join(classLabel[0])
	if classLabelx in classDict:
		values = classDict[classLabelx]
	c.write(rowA[1]+"\t"+values+"\n")

c.close()		
