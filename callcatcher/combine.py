#!/usr/bin/env python3
import sys, pickle, os, re, os.path
from . import lookup, callconfig

def loadsomething(input):
	temp = {}
	try:
		mydump = open(input, "rb")
		temp = pickle.load(mydump)
		mydump.close();
	except:
		pass
	return temp

def combine(output, inputs):
	virtualmethods = set([])
	methods = set([])
	directcalls = {}
	for input in inputs:
		input = callconfig.cachefile(input)

		tempset = loadsomething(input + 'virtualmethods.dump')
		virtualmethods = virtualmethods.union(tempset)

		tempset = loadsomething(input + 'methods.dump')
		methods = methods.union(tempset)

		tempmap = loadsomething(input + 'directcalls.dump')
		for key in tempmap:
			directcalls[key] = tempmap[key]


	mydump = open(output + 'virtualmethods.dump', 'wb')
	pickle.dump(virtualmethods, mydump)
	mydump.close()

	mydump = open(output + 'methods.dump', 'wb')
	pickle.dump(methods, mydump)
	mydump.close()

	mydump = open(output + 'directcalls.dump', 'wb')
	pickle.dump(directcalls, mydump)
	mydump.close()

if __name__ == '__main__':
	combine(sys.argv[1], sys.argv[2:])
