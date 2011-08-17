#!/usr/bin/env python

from distutils.core import setup

setup(name='callcatcher',
      version='1.1.7',
      description='Dead Code Detection',
      author='Caolan McNamara',
      author_email='caolanm@redhat.com',
      url='http://www.skynet.ie/~caolan/Packages/callcatcher.html',
      scripts=['scripts/callcatcher', 'scripts/callanalyse', 'scripts/callarchive'],
      packages=['callcatcher']
     )
