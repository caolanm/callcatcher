#!/usr/bin/env python3
import os, platform
from subprocess import Popen, PIPE

def hasprefix():
	return platform.system() == 'Darwin'
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
		if hasprefix():
			p1 = Popen('c++filt --strip-underscore', shell=True, stdin=PIPE, stdout=PIPE, close_fds=True, encoding='utf-8')
			(self.filtin1, self.filtout1) = (p1.stdin, p1.stdout)
			p2 = Popen('c++filt --no-strip-underscore', shell=True, stdin=PIPE, stdout=PIPE, close_fds=True, encoding='utf-8')
			(self.filtin2, self.filtout2) = (p2.stdin, p2.stdout)
		else:
			p1 = Popen('c++filt --no-strip-underscore', shell=True, stdin=PIPE, stdout=PIPE, close_fds=True, encoding='utf-8')
			(self.filtin1, self.filtout1) = (p1.stdin, p1.stdout)
			p2 = Popen('c++filt --strip-underscore', shell=True, stdin=PIPE, stdout=PIPE, close_fds=True, encoding='utf-8')
			(self.filtin2, self.filtout2) = (p2.stdin, p2.stdout)
	def lookup(self, name):
		print(name, file=self.filtin1)
		self.filtin1.flush()
		oldname = name
		name = self.filtout1.readline()
		name = name[:-1]
		if oldname != name:
			return symbol(name)
		print(name, file=self.filtin2)
		self.filtin2.flush()
		name = self.filtout2.readline()
		name = name[:-1]
		if oldname != name:
			return symbol(name)
		elif hasprefix():
			name = name[1:]
		return symbol(name)
	def __del__(self):
		self.filtin1.close()
		self.filtout1.close()
		self.filtin2.close()
		self.filtout2.close()
