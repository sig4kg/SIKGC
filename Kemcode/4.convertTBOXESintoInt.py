#script untuk mengubah tboxes ke format integer
import pdb
a = open("EKAW13Exp/NELLClassDict.txt")
b = open("EKAW13Exp/NELLRelationDict.txt")
t1 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX1.txt")
t2 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX2.txt")
t3 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX3.txt")
t4 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX4.txt")
t5 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX5.txt")
t6 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX6.txt")
t7 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX7.txt")
t8 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX8.txt")
t9 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX9.txt")
t10 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX10.txt")
t11 = open("../NELLWithPreCompute/TBOX/PrecomputeTBOX11.txt")


t1x = open("EKAW13Exp/TBOX1inInt.txt","w")
t2x = open("EKAW13Exp/TBOX2inInt.txt","w")
t3x = open("EKAW13Exp/TBOX3inInt.txt","w")
t4x = open("EKAW13Exp/TBOX4inInt.txt","w")
t5x = open("EKAW13Exp/TBOX5inInt.txt","w")
t6x = open("EKAW13Exp/TBOX6inInt.txt","w")
t7x = open("EKAW13Exp/TBOX7inInt.txt","w")
t8x = open("EKAW13Exp/TBOX8inInt.txt","w")
t9x = open("EKAW13Exp/TBOX9inInt.txt","w")
t10x = open("EKAW13Exp/TBOX10inInt.txt","w")
t11x = open("EKAW13Exp/TBOX11inInt.txt","w")


#make dictionary
ClassDict = {}
for lineA in a:
	rowA = lineA.split()
	#kolom 1 adalah string Class NELL 
	#kolom 2 adalah integer
	k1 = rowA[0] 
	v1 = rowA[1]
	ClassDict [k1]=v1

RelationDict = {}
for lineB in b:
	rowB = lineB.split()
	#kolom 1 adalah string relation NELL 
	#kolom 2 adalah integer
	k2 = rowB[0] 
	v2 = rowB[1]
	RelationDict[k2]=v2

strListit1 = [] 
relt1 = ""
for linet1 in t1:
	rowt1 = linet1.split()
	listt1 = rowt1[2].split("\"")
	if(rowt1[0] in RelationDict):
		relt1 = RelationDict[rowt1[0]]
	if(rowt1[1] in ClassDict):
		classDomt1 = ClassDict[rowt1[1]]

	for it1 in range(len(listt1)):
		if listt1[it1] in ClassDict:
			strListit1.append(ClassDict[listt1[it1]]+"\"")	

	strDisjointClasses = ''.join(strListit1)
	t1x.write(relt1+"\t"+classDomt1+"\t"+strDisjointClasses+"\n")
	#empty the list
	del strListit1[:]

strListit2 = [] 
relt2 = ""
classDomt2 = ""
for linet2 in t2:
	rowt2 = linet2.split()
	listt2 = rowt2[2].split("\"")	
	#pdb.set_trace()
	if(rowt2[0] in RelationDict):
		relt2 = RelationDict[rowt2[0]]
	if(rowt2[1] in ClassDict):
		classDomt2 = ClassDict[rowt2[1]]
	
	for it2 in range(len(listt2)):
		if listt2[it2] in ClassDict:
			#pdb.set_trace()
			strListit2.append(ClassDict[listt2[it2]]+"\"")	

	strDisjointClasses2 = ''.join(strListit2)
	t2x.write(relt2+"\t"+classDomt2+"\t"+strDisjointClasses2+"\n")
	#empty the list
	del strListit2[:]

for linet3 in t3:
	rowt3 = linet3.split()
	if rowt3[0] in RelationDict:
		relt3 = RelationDict[rowt3[0]]	
	t3x.write(relt3+"\n")

for linet4 in t4:
	rowt4 = linet4.split()
	if rowt4[0] in RelationDict:
		relt4 = RelationDict[rowt4[0]]	
	t4x.write(relt4+"\n")

for linet5 in t5:
	rowt5 = linet5.split()
	if rowt5[0] in RelationDict:
		relt5_1 = RelationDict[rowt5[0]]	
	if rowt5[1] in RelationDict:
		relt5_2 = RelationDict[rowt5[1]]	
	t5x.write(relt5_1+"\t"+relt5_2+"\n")

for linet6 in t6:
	rowt6 = linet6.split()
	if rowt6[0] in RelationDict:
		relt6_1 = RelationDict[rowt6[0]]	
	if rowt6[1] in RelationDict:
		relt6_2 = RelationDict[rowt6[1]]	
	t6x.write(relt6_1+"\t"+relt6_2+"\n")

for linet7 in t7:
	rowt7 = linet7.split()
	if rowt7[0] in RelationDict:
		relt7_1 = RelationDict[rowt7[0]]	
	if rowt7[1] in RelationDict:
		relt7_2 = RelationDict[rowt7[1]]	
	t7x.write(relt7_1+"\t"+relt7_2+"\n")

for linet8 in t8:
	rowt8 = linet8.split()
	if rowt8[0] in RelationDict:
		relt8 = RelationDict[rowt8[0]]	
	t8x.write(relt8+"\n")

for linet9 in t9:
	rowt9 = linet9.split()
	if rowt9[0] in RelationDict:
		relt9 = RelationDict[rowt9[0]]	
	t9x.write(relt9+"\n")

for linet10 in t10:
	rowt10 = linet10.split()
	if rowt10[0] in RelationDict:
		relt10 = RelationDict[rowt10[0]]	
	t10x.write(relt10+"\n")

for linet11 in t11:
	rowt11 = linet11.split()
	if rowt11[0] in RelationDict:
		relt11 = RelationDict[rowt11[0]]	
	t11x.write(relt11+"\n")


t1x.close()
t2x.close()
t3x.close()
t4x.close()
t5x.close()
t6x.close()
t7x.close()
t8x.close()
t9x.close()
t10x.close()
t11x.close()
