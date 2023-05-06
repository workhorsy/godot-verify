#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify


from enum import Enum
from gdtoolkit.parser import parser
from gdtoolkit.linter.ast import AbstractSyntaxTree

def parseAllSectionKeyValues(section):
	import re

	retval = {}
	heading = None
	for line in section.splitlines():
		if re.match(r"^\[\w+\]$", line):
			heading = line
		elif heading and "=" in line:
			for key, value in parseKeyValues(line).items():
				if not heading in retval:
					retval[heading] = {}
				retval[heading][key] = value

	return retval

def parseKeyValues(line):
	import re

	retval = {}

	# name = "Level"
	for match in re.findall(r'[\w_/\.]+\s*=\s*"[\s\w\.]*"', line):
		pair = list(map(lambda n: n.strip().strip('"'), match.split("=")))
		if len(pair) >= 2:
			retval[pair[0]] = pair[1]

	# singleton = false
	# NOTE: This requires brackets around "false|true" in D but not Python
	# [\w_/\.]+\s*=\s*(false|true)
	for match in re.findall(r"[\w_/\.]+\s*=\s*false|true", line):
		pair = list(map(lambda n: n.strip().strip('"'), match.split("=")))
		if len(pair) >= 2:
			retval[pair[0]] = pair[1]

	# id = 9
	for match in re.findall(r'[\w_/\.]+\s*=\s*\d+', line):
		pair = list(map(lambda n: n.strip(), match.split("=")))
		if len(pair) >= 2:
			retval[pair[0]] = pair[1]

	# total=3.97
	for match in re.findall(r'[\w_/\.]+\s*=\s*\d+\.\d+', line):
		pair = list(map(lambda n: n.strip(), match.split("=")))
		if len(pair) >= 2:
			retval[pair[0]] = pair[1]

	# instance = ExtResource( 27 )
	for match in re.findall(r'[\w_/\.]+\s*=\s*[A-Za-z]+\(\s*\d+\s*\)', line):
		pair = list(map(lambda n: n.strip(), match.split("=")))
		if len(pair) >= 2:
			retval[pair[0]] = pair[1]

	# path = "res://assets/player.png"
	for match in re.findall(r'[\w_/\.]+\s*=\s*"res://[\w/\.:]*"', line):
		pair = list(map(lambda n: n.strip().strip('"'), match.split("=")))
		if len(pair) >= 2:
			retval[pair[0]] = pair[1]

	return retval

def readFileSections(file_name):
	sections = []

	print(file_name)
	with open(file_name) as f:
		code = f.read()
	code = code.replace("\r\n", "\n")
	code = code.split("\n[")
	code = map(lambda sec: ("[" + sec).strip(), code)
	sections = list(code)

	# Remove the extra "[" from the start of the first section
	if len(sections) > 0 and sections[0].startswith("["):
		sections[0] = sections[0][1 :]
	'''
	print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
	import re
	for sec in sections:
		print("<<<<", sec, ">>>>", re.match(r"^\[node (\w|\W)*\]", sec))
	print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
	exit()
	'''
	return sections

class EntryExtResource(object):
	def __init__(self, id):
		self.id = id

class HeadingNode(object):
	def __init__(self, section):
		import helpers

		self._name = None
		self._type = None
		self._parent = None
		self._instance = None
		self._script = None

		got_heading = False
		for line in section.splitlines():
			# Node heading
			# [node name="AnimationPlayer" type="AnimationPlayer" parent="." instance=ExtResource( 3 )]
			if not got_heading and SectionType.Node == getSectionType(line):
				got_heading = True
				for key, value in parseKeyValues(line).items():
					match key:
						case "name":
							self._name = value
						case "type":
							self._type = value
						case "parent":
							self._parent = value
						case "instance":
							id = int(helpers.between(value, "ExtResource(", ")").strip())
							self._instance = EntryExtResource(id)
						case _:
							pass

			# Key value pairs under heading
			# script = ExtResource( 2 )
			if got_heading:
				for key, value in parseKeyValues(line).items():
					match key:
						case "script":
							id = int(helpers.between(value, "ExtResource(", ")").strip())
							self._script = EntryExtResource(id)
						case _:
							pass

	def isValid(self):
		return \
		self._name != None and \
		self._type != None

class HeadingConnection(object):
	def __init__(self, section):
		self._signal = None
		self._from = None
		self._to = None
		self._method = None

		got_heading = False
		for line in section.splitlines():
			# Connection heading
			# [connection signal="pressed" from="Button" to="." method="on_button_pressed"]
			if not got_heading and SectionType.Connection == getSectionType(line):
				got_heading = True
				for key, value in parseKeyValues(line).items():
					match key:
						case "signal":
							self._signal = value
						case "from":
							self._from = value
						case "to":
							self._to = value
						case "method":
							self._method = value
						case _:
							pass

	def isValid(self):
		return \
		self._signal != None and \
		self._from != None and \
		self._to != None and \
		self._method != None





class HeadingExtResource(object):
	def __init__(self, section):
		import helpers

		self._path = None
		self._type = None
		self._id = -1

		got_heading = False
		for line in section.splitlines():
			# ExtResource heading
			# [ext_resource path="res://src/ClothHolder/ClothHolder.tscn" type="PackedScene" id=21]
			if not got_heading and SectionType.ExtResource == getSectionType(line):
				got_heading = True
				for key, value in parseKeyValues(line).items():
					match key:
						case "path":
							self._path = helpers.after(value, 'res://')
						case "type":
							self._type = value
						case "id":
							self._id = int(value)
						case _:
							pass

	def isValid(self):
		return \
		self._path != None and \
		self._type != None



class SectionType(Enum):
	Unknown = 0
	Node = 1
	Connection = 2
	ExtResource = 3

def getSectionType(section):
	import re
	#print("!!!!!!!!!!!!!", section)
	if re.match(r"^\[node (\w|\W)*\]", section):
		return SectionType.Node
	elif re.match(r"^\[connection (\w|\W)*\]$", section):
		return SectionType.Connection
	elif re.match(r"^\[ext_resource (\w|\W)*\]", section):
		return SectionType.ExtResource

	return SectionType.Unknown
