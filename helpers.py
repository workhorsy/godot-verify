#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify


def before(value, separator):
	i = value.find(separator)

	if i == -1:
		return value

	return value[0 : i]

def after(value, separator):
	i = value.find(separator)

	if i == -1:
		return ""

	start = i + len(separator)

	return value[start : ]

def between(value, front, back):
	retval = after(value, front)
	retval = before(retval, back)
	return retval
