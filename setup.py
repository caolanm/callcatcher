#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='callcatcher',
      version='1.2.0',
      description='Dead Code Detection',
      author='Caolán McNamara',
      author_email='caolanm@redhat.com',
      url='http://www.skynet.ie/~caolan/Packages/callcatcher.html',
      scripts=['scripts/callcatcher', 'scripts/callanalyse', 'scripts/callarchive', 'scripts/callcatcher-CC', 'scripts/callcatcher-CXX', 'scripts/callcatcher-AR'],
      packages=['callcatcher']
     )
