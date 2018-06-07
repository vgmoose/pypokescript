# misc utils used in other classes

# make value -> key pairs in incoming dict
def doublyLink(m):
	keys = list(m.keys())
	vals = list(m.values())
	for x in range(len(keys)):
		if type(vals[x]) is tuple:
			m[vals[x][0]] = keys[x]
		else:
			m[vals[x]] = keys[x]

# convert bytes to a string, and also swap both bytes
def s(a):
	if type(a) is str:
		a = int(a, 16)
	return bytes.fromhex("%04x" % ((a >> 8) | ((a & 0x00FF) << 8)))
