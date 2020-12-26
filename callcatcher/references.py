#!/usr/bin/env python3
import sys, pickle, os, re, os.path
from . import lookup

class CollectReferences:
	def __init__(self):
		self.directcalls = {}
	def savedb(self, file):
		mydump = open(file + 'directcalls.dump', 'wb')
		pickle.dump(self.directcalls, mydump)
		mydump.close();
	def handleaddrtake(self, called, aLookup):
#		print('called is ' + called)
		name = ''
		if len(called) > 2 and called.find('+') == -1:
			parts = called.split(',')
			if len(parts) > 1:
				name = parts[0]
#				print('name is ' + name)
		if name != '' and not name[1:].isdigit():
			if name[0] == '$':
				name = name[1:]
#			print('name is now ' + name)
			end = 0
			if name.find('%') != -1 and name[-1:] == ')':
				end = len(name) - 1
				while (end > 0) and name[end] != '(':
					end = end - 1
			if end > 1:
				name = name[:end]

			name = aLookup.lookup(name)
#			print('final name is ' + name)
			self.directcalls[name] = 2
	def collect(self, inputfile):
		input = open(inputfile, 'r')

		aLookup = lookup.Lookup()

		callre = re.compile("	call	")
		move32re = re.compile("	movl	")
		move64re = re.compile("	movq	")
		cmovre = re.compile("	cmovne	")
		and32re = re.compile("	andl	")
		and64re = re.compile("	andq	")
		lea32re = re.compile("	leal	")
		lea64re = re.compile("	leaq	")
		data32re = re.compile("	.long	")
		data64re = re.compile("	.quad	")
		jumpre = re.compile("	jmp	")
		push32re = re.compile("	pushl	")
		push64re = re.compile("	pushq	")

		while 1:
			foobar = input.readline()
			if foobar == "":
				break
			foobar = foobar[:-1]
			if data32re.match(foobar) or data64re.match(foobar):
				name = ''
				called = foobar[7:].strip()
				if called != '' and not called[1:].isdigit():
					called = aLookup.lookup(called)
					self.directcalls[called] = 3
			elif move32re.match(foobar) or lea32re.match(foobar) or and32re.match(foobar) or move64re.match(foobar) or lea64re.match(foobar) or and64re.match(foobar):
				called = foobar[6:].strip()
				self.handleaddrtake(called, aLookup)
			elif cmovre.match(foobar):
				called = foobar[8:].strip()
				self.handleaddrtake(called, aLookup)
			elif callre.match(foobar):
				called = foobar[6:].strip()
				if called[:2] != '*%':
					called = aLookup.lookup(called)
					self.directcalls[called] = 1
			elif jumpre.match(foobar):
				called = foobar[5:].strip()
				if called[:2] != '*%':
					called = aLookup.lookup(called)
					self.directcalls[called] = 1
			elif push32re.match(foobar) or push64re.match(foobar):
				called = foobar[7:].strip()
				if called[0] == '-' or ((called[0] <= '9') and (called[0] >= '0')):
					continue
				end = len(called) - 1
				while (end > 0) and called[end] != '(':
					end = end - 1
				if end > 1:
					called = aLookup.lookup(called[:end])
					self.directcalls[called] = 1

		self.savedb(inputfile)
