#script for counting predicats in the end of Iteration
a = open("RuleFlow2/endOfIteration/NewTriplesInIteration1.txt")

seen = set()
count = 0
for line in a:
	row = line.split()
	if(row[1] not in seen):
		seen.add(row[1])
		count += 1

print count
