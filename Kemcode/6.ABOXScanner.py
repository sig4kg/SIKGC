#script untuk membuat array 2 dimensi dari data NELL
#every line in nell consist of 6 columns
#column 0 until 2 is empty string, column 3, 4 and 5 contain the values
import time
start = time.time()
import pdb
a = open("EKAW13Exp/_newTriplesinInt.txt")
b = open("EKAW13Exp/TBOX1inInt.txt")
t2 = open("EKAW13Exp/TBOX2inInt.txt")
t3 = open("EKAW13Exp/TBOX3inInt.txt")
t4 = open("EKAW13Exp/TBOX4inInt.txt")
t5 = open("EKAW13Exp/TBOX5inInt.txt")
t6 = open("EKAW13Exp/TBOX6inInt.txt")
t7 = open("EKAW13Exp/TBOX7inInt.txt")
t8 = open("EKAW13Exp/TBOX8inInt.txt")
t9 = open("EKAW13Exp/TBOX9inInt.txt")
t10 = open("EKAW13Exp/TBOX10inInt.txt")
t11 = open("EKAW13Exp/TBOX11inInt.txt")
x = open("EKAW13Exp/Instance_Class.txt")

notValid = open("EKAW13Exp/NotValid.txt","w")
unknown = open("EKAW13Exp/Unknown.txt","w")

#initialise 2 dimensional array for NELL
arrayNELL = [["" for j in range(0,3)]for i,lineA in enumerate(a)]

a.seek(0,0)
for i,lineA in enumerate(a):	
	rowA = lineA.split()
	for j in range(0,3):
		arrayNELL[i].append(rowA[j])
#now, arrayNELL contain all the triples in 2 dimensional form and in integer format

#we use instance_classDictionary, see the format
#6 90 (6 is ID of instance, while 90 is ID of class)
instance_classDictionary={}
for lineX in x:
	rowX = lineX.split()	
	k = rowX[0]
	v = rowX[1]
	instance_classDictionary[k]=v

#b adalah tbox1 dalam format integer
for lineB in b:	
	rowB = lineB.split() #rowB[0] adalah nama relasi
	#rowB[1] adalah domain
	#rowB[2] adalah list of disjoint classes
	listB = rowB[2].split("\"")
	found = 0	
	for i in range(len(arrayNELL)):
		#pdb.set_trace()
		if(rowB[0]==arrayNELL[i][4]):
			#take the head of Instance (in integer)
			headInstance = arrayNELL[i][3]
			#pdb.set_trace()
			#traverse the instance_classDictionary, looking for ClassID for headInstance			
			if(headInstance in instance_classDictionary):
				classLabel = instance_classDictionary[headInstance]
				for j in range(0,len(listB)):
					if(classLabel==listB[j]):
						#pdb.set_trace()	
						found = 1
						notValid.write(arrayNELL[i][3]+"\t"+arrayNELL[i][4]+"\t"+arrayNELL[i][5]+"\n")
						break #keluar dari for
				if(found==1):	
					found=0					
				else: #found = 0 karena classLabel tidak ada di dalam list
					#If we can not find the class label in list of A and if it is not the 
					#same with the domain of r then it is unknown.
					if(classLabel!=rowB[1]):
						#pdb.set_trace()
						unknown.write(arrayNELL[i][3]+"\t"+arrayNELL[i][4]+"\t"+arrayNELL[i][5]+"\n")
t1time = time.time()
endt1 = t1time-start
print endt1
#t2 adalah tbox 2
for lineT2 in t2:
	rowT2 = lineT2.split() #rowT2[0] adalah nama relasi
	#rowT2[1] adalah range
	#rowT2[2] adalah list of disjoint classes
	listT2 = rowT2[2].split("\"")
	found = 0
	for i2 in range(len(arrayNELL)):
		if(rowT2[0]==arrayNELL[i2][4]):
			#take the tail of Instance
			tail = arrayNELL[i2][5]
			#traverse the instance_classDictionary, looking for ClassID for tail			
			if(tail in instance_classDictionary):
				classLabel = instance_classDictionary[tail]						
				for j2 in range(0,len(listT2)):
					if(classLabel==listT2[j2]):
						#pdb.set_trace()	
						found = 1
						notValid.write(arrayNELL[i2][3]+"\t"+arrayNELL[i2][4]+"\t"+arrayNELL[i2][5]+"\n")
						break #keluar dari for
				if(found==1):	
					found=0					
				else: #found = 0 karena classLabel tidak ada di dalam list
					#If we can not find the class label in list of A and if it is not the 
					#same with the range of r then it is unknown.
					if(classLabel!=rowT2[1]):
						unknown.write(arrayNELL[i2][3]+"\t"+arrayNELL[i2][4]+"\t"+arrayNELL[i2][5]+"\n")
t2time = time.time()
endt2 = t2time-t1time
print endt2
#t3 adalah tbox 3
for lineT3 in t3:
	rowT3 = lineT3.split() 
	#t3 hanya punya 1 kolom yaitu id relasi
	for i3 in range(len(arrayNELL)):
		if(rowT3[0]==arrayNELL[i3][4]):
			notValid.write(arrayNELL[i3][3]+"\t"+arrayNELL[i3][4]+"\t"+arrayNELL[i3][5]+"\n")
			#tidak dibreak, karena kita masih mencari triple lain di arrayNELL yang mengandung r sebagai predikatnya
t3time = time.time()
endt3 = t3time-t2time
print endt3
#t4 adalah tbox 4
for lineT4 in t4:
	rowT4 = lineT4.split() 
	#t4 hanya punya 1 kolom yaitu nama relasi
	for i4 in range(len(arrayNELL)):
		if(rowT4[0]==arrayNELL[i4][4]):
			notValid.write(arrayNELL[i4][3]+"\t"+arrayNELL[i4][4]+"\t"+arrayNELL[i4][5]+"\n")
			#tidak dibreak, karena kita masih mencari triple lain di arrayNELL yang mengandung r sebagai predikatnya
t4time = time.time()
endt4 = t4time-t3time
print endt4		

#t8 adalah tbox 8
dict_11 = {}
for i11,line11 in enumerate(t11):
	row11 = line11.split()	
	k11 = row11[0]
	v11 = i11
	dict_11[k11] = v11
dict_abox = {}
a.seek(0,0)
for iBox,lineBox in enumerate(a):	
	kBox = lineBox
	vBox = iBox
	dict_abox[kBox] = vBox
dict_8 = {}
for i8,line8 in enumerate(t8):
	row8 = line8.split()	
	k8 = row8[0]
	v8 = i8
	dict_8[k8] = v8

lineCompare=""
a.seek(0,0)
for lineA8 in a:
	rowA8 = lineA8.split()	
	if(rowA8[1] in dict_11):
		#it means this property is irreflexive, 
		#check for this pattern in a
		if(rowA8[0]==rowA8[2]):
			notValid.write(rowA8[0]+"\t"+rowA8[1]+"\t"+rowA8[2]+"\n")

	#check the symmetric tbox
	if(rowA8[1] in dict_8):
		#it means this property is asymmetric, 
		#check dict_abox

		lineCompare = rowA8[2]+"\t"+rowA8[1]+"\t"+rowA8[0]+"\n"
		if(lineCompare in dict_abox): 
			notValid.write(rowA8[0]+"\t"+rowA8[1]+"\t"+rowA8[2]+"\n")
			notValid.write(rowA8[2]+"\t"+rowA8[1]+"\t"+rowA8[0]+"\n")

t8time = time.time()
endt8 = t8time-t4time
print endt8
#t9 adalah tbox 9
for lineT9 in t9:
	rowT9 = lineT9.split() 
	#t9 hanya punya 1 kolom yaitu nama relasi
	for i9 in range(len(arrayNELL)):
		if(rowT9[0]==arrayNELL[i9][4]):
			notValid.write(arrayNELL[i9][3]+"\t"+arrayNELL[i9][4]+"\t"+arrayNELL[i9][5]+"\n")
			#tidak dibreak, karena kita masih mencari triple lain di arrayNELL yang mengandung r sebagai predikatnya

t9time = time.time()
endt9 = t9time-t8time
print endt9
#t10 adalah tbox 10
for lineT10 in t10:
	rowT10 = lineT10.split() 
	#t10 hanya punya 1 kolom yaitu nama relasi
	for i10 in range(len(arrayNELL)):
		if(rowT10[0]==arrayNELL[i10][4]):
			notValid.write(arrayNELL[i10][3]+"\t"+arrayNELL[i10][4]+"\t"+arrayNELL[i10][5]+"\n")
			#tidak dibreak, karena kita masih mencari triple lain di arrayNELL yang mengandung r sebagai predikatnya



notValid.close()
unknown.close()

end = time.time()
interval = end-start
print interval
					
	
