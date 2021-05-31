a = open("EKAW13Exp/NotValid.txt")
b = open("EKAW13Exp/NotValidWD.txt","w")

seen = set()
for line in a:
	if line not in seen:
		seen.add(line)
		b.write(line)

b.close()
