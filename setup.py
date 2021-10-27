#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='callcatcher',
      version='1.2.1',
      description='Dead Code Detection',
      author='Caolán McNamara',
      author_email='caolanm@redhat.com',
      url='http://www.skynet.ie/~caolan/Packages/callcatcher.html',
      scripts=['scripts/callcatcher', 'scripts/callanalyse', 'scripts/callarchive'],
      packages=['callcatcher']
     )
