#!/bin/env python
import os

def symbol(name):
	index = name.find('@PLT')
	if index != -1:
		name = name[:index]
	index = name.find('@GOT')
	if index != -1:
		name = name[:index]
	index = name.find('@GOTOFF')
	if index != -1:
		name = name[:index]
	return name
def typeinfo(name):
	if name.find('typeinfo ') == -1:
		return False
	return True
def vtablename(name):
	return name[11:]

class vtable:
	def __init__(self, classowner):
		self.classowner = classowner
		self.vmethods = {}
		self.parents = []

class virtualmethod:
	def __init__(self, classowner, name, offset):
		self.classowner = classowner
		self.name = name
		self.offset = offset

class Lookup:
	def __init__(self):
		self.filtin1, self.filtout1 = os.popen2('c++filt --no-strip-underscore', 'rw')
		self.filtin2, self.filtout2 = os.popen2('c++filt --strip-underscore', 'rw')
	def lookup(self, name):
		print >> self.filtin1, name
		self.filtin1.flush()
		oldname = name
		name = self.filtout1.readline()
		name = name[:-1]
		if oldname <> name:
			return symbol(name)
		print >> self.filtin2, name
		self.filtin2.flush()
		name = self.filtout2.readline()
		name = name[:-1]
		return symbol(name)
	def __del__(self):
		self.filtin1.close()
		self.filtout1.close()
		self.filtin2.close()
		self.filtout2.close()
