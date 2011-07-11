#!/usr/bin/python
import re, os.path, pickle, lookup, callconfig, combine, fnmatch

OOoMacros = [
  '::_ForEach\(', 
  '::Replace\(', 
  '::Remove\(', 
  '::Insert\(', 
  '::DeleteAndDestroy\(', 
  '::GetPos\(', 
  '::LinkStub', 
  '::impl_createFactory\(', 
  '::impl_createInstance\(', 
  '::GetChildWindowId\(', 
  '::RegisterControl\(', 
  '::Init\(', 
  '::Exit\(',
  '::RegisterChildWindow\(',
  'Shell::CreateObject\(',
  'cppu_detail_getUnoType' ]
OOoUNOEntryPoints = [
  '^component_canUnload$', 
  '^component_getDescriptionFunc$', 
  '^component_getFactory$', 
  '^component_getImplementationEnvironment$', 
  '^component_writeInfo$' ]
OOoDLLEntryPoints = [
  '^GetVersionInfo$',
  '^Create.+DocShellDll$',
  '^Init.+Dll$',
  '^DeInit.+Dll$',
  '^CreateDialogFactory$',
  'Sal_queryFaxNumber' ]
OOoBuiltInEntryPoints = [
  '^__builtin_delete$',
  '^__builtin_new$',
  '^__builtin_vec_delete$',
  '^__builtin_vec_new$',
  '^__pure_virtual$' ]
OOoMozillaEntryPoints = [
  '^NPP_'
]
OOoMISCEntryPoints = [
  '^getSvtAccessibilityComponentFactory$',
  '^getStandardAccessibleFactory$',
  '^dbg_dump',
  '^debug_oustring',
  '^Sal_SetupPrinterDriver',
  '^Sal_authenticateQuery',
  '^add_to_recently_used_file_list$',
  '^Java_com_sun_star_lib_connections_pipe_PipeConnection_createJNI$',
  '^Java_com_sun_star_lib_connections_pipe_PipeConnection_closeJNI$',
  '^Java_com_sun_star_lib_connections_pipe_PipeConnection_readJNI$',
  '^Java_com_sun_star_lib_connections_pipe_PipeConnection_writeJNI$',
  '^Java_com_sun_star_lib_connections_pipe_PipeConnection_flushJNI$',
  '^ExportDOC$',
  '^ExportRTF$',
  '^ExportPPT$',
  '^ImportDOC$',
  '^ImportRTF$',
  '^ImportPPT$',
  '^SaveVBA$',
  '^GetSaveWarningOfMSVBAStorage_ww8$',
  '^SaveOrDelMSVBAStorage_ww8$',
  '^SchGetChartData$',
  '^SchConvertChartRangeForWriter$',
  '^SchGetDefaultForColumnText$',
  '^SchGetDefaultForRowText$',
  '^SchMemChartInsertCols$',
  '^SchMemChartInsertRows$',
  '^SchMemChartRemoveCols$',
  '^SchMemChartRemoveRows$',
  '^SchUpdateAttr$',
  'insertExtensionXcsFile',
  'insertExtensionXcuFile',
  'insertModificationXcuFile'
]
flexEntryPoints = [
  'yy_flex_strlen',
  'yy_scan_string',
  'yyget_debug',
  'yyget_in',
  'yyget_leng',
  'yyget_lineno',
  'yyget_out',
  'yyget_text',
  'yyinput',
  'yylex_destroy',
  'yypush_buffer_state',
  'yyset_debug',
  'yyset_in',
  'yyset_lineno',
  'yyset_out',
  'yyunput'
]
xpdfEntryPoints = [
  'mapUCS2'
]
OOoIgnoreRE = OOoMacros + OOoUNOEntryPoints + OOoDLLEntryPoints + OOoBuiltInEntryPoints + OOoMozillaEntryPoints + OOoMISCEntryPoints + xpdfEntryPoints
OOoIgnore = []
for item in OOoIgnoreRE:
	OOoIgnore.append(re.compile(item))

flexIgnore = []
for item in flexEntryPoints:
	flexIgnore.append(re.compile(item))

def compatrsplit(s, sep, maxsplits=0):
    """Like str.rsplit, which is Python 2.4+ only."""
    L = s.split(sep)
    if not 0 < maxsplits <= len(L):
        return L
    return [sep.join(L[0:-maxsplits])] + L[-maxsplits:]

def calliscopyctor(call):
        call = call.replace("(anonymous namespace)", "")
        call = call.replace("dbaxml::ODBExport::exportDataSource()::", "")

        endofname = call.find('(')
        if endofname != -1:
                name = call[0:endofname]
                foo = name.split('::')
                if len(foo) > 1:
                        methodname = foo[len(foo)-1]
                        if methodname == foo[len(foo)-2]:
                                classname = compatrsplit(name, '::', 1)[0]
                                copyctor = classname + '::' + methodname + '(' + classname + ' const&)'
                                if copyctor == call:
                                        return True
        return False
	
def readmapfile(mapfile):
	if not len(mapfile):
		return []

	input = open(mapfile)
	globals = []
	add = False
	while 1:
		foobar = input.readline()
		if foobar == "":
			break

		foobar = foobar.strip()
		if not len(foobar):
			continue
		foobar = foobar.split('#')[0]
		if not len(foobar):
			continue

		if foobar == "global:":
			add = True
			continue
		elif foobar == "local:":
			add = False
			continue
		elif foobar[0] == "}":
			add = False
			continue
	
		if not add:
			continue

		while len(foobar):
			result = foobar.partition(';')
			if result[1] != ';':
				break
			foobar = result[0]
			globals.append(foobar.strip())
			foobar = result[2].strip()

	return globals

def convertall(methods):
    ret = set([])
    aLookup = lookup.Lookup()
    for a in methods:
        ret.add(aLookup.lookup(a))
    return ret

def removemapped(methods, mapfileexports):
    matched = set([])
    for pattern in mapfileexports:
	for a in methods:
	    if (fnmatch.fnmatch(a, pattern)):
                matched.add(a)
    return methods.difference(matched)

def analyse(output, prefix = "", strict = False, detailed = False, OOo = False, mapfile=""):
	mydump = open(output + 'directcalls.dump', 'r')
	directcalls = pickle.load(mydump)
	mydump.close();

	mydump = open(output + 'methods.dump', 'r')
	methods = pickle.load(mydump)
	mydump.close();

	mydump = open(output + 'virtualmethods.dump', 'r')
	virtualmethods = pickle.load(mydump)
	mydump.close();

        mapfileexports = readmapfile(mapfile)

	if detailed:
		print prefix + '---Referenced symbols---'
		for call in directcalls:
			type = directcalls[call]
			if type == 1:
				print prefix + call + ' is directly called'
			elif type == 3:
				print prefix + call + ' is used in data'
			else:
				print prefix + call + ' has its address taken'
                if len(mapfile):
			print prefix + '---Global symbols in mapfile---'
			for call in mapfileexports:
				print prefix + call + ' is set as global in mapfile'
		print prefix + '---Unreferenced symbols---'

	methods = removemapped(methods, mapfileexports)
        methods = convertall(methods)
        virtualmethods = convertall(virtualmethods)

	uncalled = []
	for call in methods:
		if not directcalls.has_key(call) and not call in virtualmethods:
			uncalled.append(call)
	uncalled.sort()

	for call in uncalled:
		if strict:
			print prefix + call
		else:
			acceptable = True
			if call == 'main' or call == '_main':
				acceptable = False
			elif call.find('operator') != -1:
				acceptable = False
			elif call.find('virtual thunk') != -1:
			        acceptable = False

			if acceptable:
				parts = call.split('::', 1)
				if len(parts) > 1:

					#having well formed copy constructors should be encouraged
					if calliscopyctor(call):
						acceptable = False

					#if we have an unused const varient, but a used nonconst varient or
					#vice versa, that should be encouraged
					if acceptable:
						if call.rfind(' const') == len(call) - 6:
							reverse = call[:-6]
						else:
							reverse = call + ' const'
						
						if directcalls.has_key(reverse):
							acceptable = False

			if OOo and acceptable:
				for item in OOoIgnore:
					if item.search(call):
						acceptable = False
						break

			if acceptable:
				for item in flexIgnore:
					if item.search(call):
						acceptable = False
						break

			if acceptable:
				print prefix + call
