#!/bin/env python
import sys, pickle, re, lookup, os.path, os

class CollectDefines:
	def __init__(self):
		self.methods = set([])
		self.virtualmethods = set([])
	def savedb(self, file):
		mydump = open(file + 'methods.dump', 'w')
		pickle.dump(self.methods, mydump)
		mydump.close();

		mydump = open(file + 'virtualmethods.dump', 'w')
		pickle.dump(self.virtualmethods, mydump)
		mydump.close();
	def collect(self, inputname):
		input = open(inputname, 'r')
	
		aLookup = lookup.Lookup()

		definere = re.compile(".*:$")
	
		lastline=''
		foobar=''
		invtable = False
		while 1:
			lastline = foobar
			foobar = input.readline()
			if len(foobar) < 2:
				break
			foobar = foobar[:-1]
			if invtable and foobar[0] != '\t':
				invtable = False 

			if invtable:
				if foobar.find('	.long	') != -1 or foobar.find('	.quad	') != -1:
					name = foobar[7:]
					if name[0] != '0':
						virtualname = aLookup.lookup(name)
						if not lookup.typeinfo(virtualname):
							self.virtualmethods.add(name)
			elif foobar[0] != '.' and definere.match(foobar):
				foobar = foobar[:-1]
				name = foobar

				realname = aLookup.lookup(name)

				if lookup.typeinfo(realname):
					continue
				elif realname.find('vtable for') != -1:
					invtable = True
				else:
					type = lastline.split('@')
					if len(type) == 2 and type[1] == 'function':
						self.methods.add(name)
					else:
						type = lastline.split()
						if len(type) == 7 and type[0] == '.def' and type[2] == '.scl' and type[3] == '2;' and type[4] == '.type' and type[5] == '32;' and type[6] == '.endef':
							self.methods.add(name) 	
		self.savedb(inputname)

		for key in self.methods:
			if not key in self.virtualmethods:
				print '\t\tnon-virtual', aLookup.lookup(key)

		for key in self.methods:
			if key in self.virtualmethods:
				print '\t\tvirtual', aLookup.lookup(key)
