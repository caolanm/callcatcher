#!/usr/bin/python2
import os, os.path, shutil, sys
import defines, references, callconfig, combine, analyse

def abslinkoutput(input):
	file = 'a.out'
	if input.count('-o'):
		index = input.index('-o')
		file = input[index + 1]
	elif input.count('-r'):
		index = input.index('-r')
		file = input[index + 1]
	return os.path.abspath(file)

def outputindex(input):
	if input.count('-o'):
		return input.index('-o') + 1
	else:
		return -1

def makecachedir(file):
	dir = os.path.split(file)[0]
	try:
		os.makedirs(dir)
	except:
		pass

def getinputfile(args):
	ret = ''
	i = 1
	while i < len(args):
		arg = args[i]
		if arg == '-o' or arg == '-MF' or arg == '-MT' or arg == '-MQ' or arg == '-isystem':
			i = i + 1
		elif arg[0] != '-':
			if ret != "":
				print >> sys.stderr, "callcatcher: multiple input files in one invocation currently unsupported, FIXME", ret, arg, args
				return ""
			ret = arg
		i = i + 1
	return ret

def getoutputfile(args):
	index = outputindex(args)
	if index != -1:
		return args[index], index
	arg = getinputfile(args)
	name, suffix = os.path.splitext(arg)
	return name + '.o', -1

def shellquote(arg):
    return "'" + arg.replace("'", "'\\''") + "'"

def compile(args):
	realinput = getinputfile(args)

	if realinput == "":
		return

	name, suffix = os.path.splitext(realinput)
	realoutput , index = getoutputfile(args)

	print "callcatcher - detecting compiling: \n\tcollecting", \
		realoutput

	#map original gcc output file to scraped intermediate .s
	filename = callconfig.cachefile(realoutput)
	makecachedir(filename)

	if suffix == '.s':
		#force an intermediate copy of .s file
		#for the rare case of an input .s file
		shutil.copyfile(realinput, filename)
		print 'Copying', realinput, 'to', filename
	else:
		if index != -1:
			args[index] = filename
		else:
			args.append('-o')
			args.append(filename)

		program = ''
		for arg in args:
			if len(arg) > 2 and arg[0:2] == '-O':
				continue
			program = program + ' ' + shellquote(arg)
		#force an intermediate assemble
		program = program + ' ' + shellquote('-O0') + ' ' + shellquote('-S')
		print program
		errret = os.system(program)
		if errret != 0:
			return

	#collect non-virtual method/function declarations
	aDefines = defines.CollectDefines()
	aDefines.collect(filename)

	#collect non-virtual method/function calls
	aReferences = references.CollectReferences()
	aReferences.collect(filename)

	os.remove(filename)

	print '\t', len(aDefines.methods), 'methods', '(' + str(len(aDefines.virtualmethods)) + \
		' virtual)'

def link(args):
	realoutput = abslinkoutput(args)
	output = callconfig.cachefile(realoutput)
	inputs = []
	fakeargs = [ args[0], ]
	uncompiled = []
	skip = False
	for arg in args[1:]:
		if skip:
			skip = False
			continue
		if arg[0] == '-' and len(arg) > 1 and arg[1] != 'o':
			if arg[1] == 'l':
				print 'linking against lib' + arg[2:] + '[.so|.a]'
			fakeargs.append(arg)
		elif arg == '-o':
			skip = True
		else:
			name, suffix = os.path.splitext(arg)
			if suffix == '.c' or suffix == '.cc' \
				or suffix == '.cp' or suffix == '.cxx' \
				or suffix == '.cpp' or suffix == '.CPP' \
				or suffix == '.c++' or suffix == '.C' \
				or suffix == '.s':
				inputs.append(name + '.o')
				uncompiled.append(arg)
			else:
				inputs.append(arg)

	if len(uncompiled):
		print 'callcatcher - linkline contains source files, forcing',\
			'compile of:'
		print '\t', uncompiled
		fakeargs.append('-c')
		for uncompile in uncompiled:
			compileline = fakeargs
			compileline.append(uncompile)
			compile(compileline)

	if not len(inputs):
		return

	makecachedir(output)
	print "callcatcher - detecting link:"
	print "\tautojoining", \
		realoutput, "from\n\t", inputs
	combine.combine(output, inputs)
	print "callcatcher - dump currently unused:"
	print "\tUse \"callanalyse\" to manually analyse a set of compiler output files"
	print "\tautoanalysing", realoutput
	print "\tCurrently unused functions are..."
	analyse.analyse(output, "\t\t")

def archive(args):
	realoutput = ''
	output = ''
	inputs = []
	uncompiled = []
	skipping = True;
	for arg in args[1:]:
		if len(realoutput) == 0 and (arg[0] == '-' or len(arg) == 1):
			continue;
		elif (len(realoutput) == 0):
			realoutput = os.path.abspath(arg)
			output = callconfig.cachefile(realoutput)
		else:
			inputs.append(arg)

	if not len(inputs):
		return

	makecachedir(output)
	print "callcatcher - detecting archiving:"
	print "\tautojoining", \
		realoutput, "from\n\t", inputs
	combine.combine(output, inputs)
	print "callcatcher - dump currently unused:"
	print "\tUse \"callanalyse\" to manually analyse a set of compiler output files"
	print "\tautoanalysing", realoutput
	print "\tCurrently unused functions are..."
	analyse.analyse(output, "\t\t")
