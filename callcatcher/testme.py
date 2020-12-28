#!/usr/bin/env python3

example1 = "binfilter::E3dObjList::E3dObjList(binfilter::E3dObjList const&)";
example2 = "E3dObjList::E3dObjList(E3dObjList const&)";
example3 = "E3dObjList::E3dObjList(foo const&)";

def compatrsplit(s, sep, maxsplits=0):
    """Like str.rsplit, which is Python 2.4+ only."""
    L = s.split(sep)
    if not 0 < maxsplits <= len(L):
        return L
    return [sep.join(L[0:-maxsplits])] + L[-maxsplits:]

def calliscopyctor(call):
	endofname = call.find('(')
	if endofname != -1:
		name = call[0:endofname]
		print('name is', name)
		foo = name.split('::')
		if len(foo) > 1:
			methodname = foo[len(foo)-1]
			if methodname == foo[len(foo)-2]:
				classname = compatrsplit(name, '::', 1)[0]
				print('constructor argument is', classname)
				print('methodname is', methodname)
				copyctor = classname + '::' + methodname + \
					'(' + classname + ' const&)'
				print(copyctor)
				if copyctor == call:
					print('yes')


calliscopyctor(example1)
calliscopyctor(example2)
calliscopyctor(example3)
