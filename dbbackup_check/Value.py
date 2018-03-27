#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Value:
    	def __init__ (self, value):
    	    '''Parses the value.'''
    	    if str (value) [-1:] in ('K', 'M', 'G', 'T'):
    	        self.__int = int (value [:-1])
    	        self.__unit = value [-1:]
    	    else:
    	        self.__int = int (value)
    	        self.__unit = None

    	def __str__ (self):
    	    '''If necessary changes the value to number + unit format by rounding.'''
    	    if self.__unit:
    	        return str (self.__int) + self.__unit
    	    if self.__int > 10 ** 12:
    	        return str (round (self.__int / 10 ** 12)) [:-2] + 'T'
    	    if self.__int > 10 ** 9:
    	        return str (round (self.__int / 10 ** 9)) [:-2] + 'G'
    	    if self.__int > 10 ** 6:
    	        return str (round (self.__int / 10 ** 6)) [:-2] + 'M'
    	    if self.__int > 10 ** 3:
    	        return str (round (self.__int / 10 ** 3)) [:-2] + 'K'
    	    return str (self.__int)

    	def __int__ (self):
    	    '''If necessary changes the value to number format.'''
    	    if self.__unit == 'K':
    	        return self.__int * 10 ** 3
    	    if self.__unit == 'M':
    	        return self.__int * 10 ** 6
    	    if self.__unit == 'G':
    	        return self.__int * 10 ** 9
    	    if self.__unit == 'T':
    	        return self.__int * 10 ** 12
    	    return self.__int

    	def __cmp__ (self, other):
    	    return cmp (int (self), int (other))

