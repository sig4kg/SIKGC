#script for comparing the KG from end of iteration with the KG from previous iteration
#iteration 1
#a = open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/ComparingLCWithGCOnOriData/PBRNewDisjoint/NELLInitialValidNew.txt")
#b = open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/ISWC2018/IC3-Iteration1/_all4PBRcheckingFix.txt")
#new = open("IC3-Iteration1/NewTriplesInIteration1.txt","w") 

#iteration 2: Iteration2.txt merupakan kombinasi dari PBRValid+Materialization
#a = open("IC3Flow1-Ite2/endOfIteration/Input.txt")
#b = open("IC3Flow1-Ite2/endOfIteration/Iteration2V2.txt")
#new = open("IC3Flow1-Ite2/endOfIteration/NewTriplesInIteration2V2.txt","w") 

#iteration 1 of Experiment on materialisation flow 1
#a = open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/ComparingLCWithGCOnOriData/PBRNewDisjoint/NELLInitialValidNew.txt")
#b = open("Ex6.3onMaterialisation/endOfIteration/iteration1.txt")
#new = open("Ex6.3onMaterialisation/endOfIteration/NewTriplesInIteration1.txt","w") 

#iteration 1 of Experiment on materialisation flow 2
#a = open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/ComparingLCWithGCOnOriData/PBRNewDisjoint/NELLInitialValidNew.txt")
#b = open("Ex6.3onMatFlow2/endOfIteration/Iteration2.txt")
#new = open("Ex6.3onMatFlow2/endOfIteration/NewTriplesInIteration1.txt","w") 

#iteration 1 of Experiment on Rule flow 1
#a = open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/ComparingLCWithGCOnOriData/PBRNewDisjoint/NELLInitialValidNew.txt")
#b = open("RuleFlow1/endOfIteration/_iteration1WithConcept.txt")
#new = open("RuleFlow1/endOfIteration/NewTriplesInIteration1.txt","w") 

#iteration 1 of Experiment on Rule flow 2
#a = open("/home/rpgsbs/r01krw16/KGCTools/KemScript/_NELL-995Iteration/ComparingLCWithGCOnOriData/RawTriplesWithoutAsymmetric.txt")
#b = open("_Ev6.3/1stIteration/endOfIteration/_iteration1WithConcept.txt")
#new = open("_Ev6.3/1stIteration/endOfIteration/NewTriplesCompareWithKG0.txt","w") 

#iteration 2 of Experiment on Rule flow 2
a = open("_Ev6.4RuleFlow2/2ndIteration/endOfIteration/InputIte2.txt")
b = open("_Ev6.4RuleFlow2/2ndIteration/endOfIteration/OutputIteration2.txt")
new = open("_Ev6.4RuleFlow2/2ndIteration/endOfIteration/NewTriplesIte2.txt","w") 

#iteration 2 of Experiment on Rule Flow 1 
#a = open("RuleFlow1/Iteration2/endOfIteration/Input.txt")
#b = open("RuleFlow1/Iteration2/endOfIteration/Iteration2.txt")
#new = open("RuleFlow1/Iteration2/endOfIteration/NewTriples.txt","w")

#iteration 3 of Experiment on Rule Flow 1 
#a = open("RuleFlow1/Iteration3/endOfIteration/Input.txt")
#b = open("RuleFlow1/Iteration3/endOfIteration/Iteration3.txt")
#new = open("RuleFlow1/Iteration3/endOfIteration/NewTriples.txt","w")

#iteration 2 of Experiment on Mate Flow 2 
#a = open("MateFlow2/Iteration2/endOfIteration/InputIte2.txt")
#b = open("MateFlow2/Iteration2/endOfIteration/Iteration2.txt")
#new = open("MateFlow2/Iteration2/endOfIteration/NewTriples.txt","w")

#iteration 2 of Experiment on Mate Flow 1 
a = open("MateFlow1/Iteration2/endOfIteration/InputIte2.txt")
b = open("MateFlow1/Iteration2/endOfIteration/outputIte2RUMIS.txt")
new = open("MateFlow1/Iteration2/endOfIteration/NewTriples.txt","w")


dictOld = {}
for iA,lineA in enumerate(a):
	kA = lineA
	vA = iA
	dictOld[kA] = vA

for lineB in b:
	if(lineB not in dictOld):	
		new.write(lineB)

new.close()

