#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify

from enum import Enum
from gdtoolkit.parser import parser
from gdtoolkit.linter.ast import AbstractSyntaxTree

def before(value, separator):
	i = value.find(separator);

	if i == -1:
		return value

	return value[0 : i]

def after(value, separator):
	i = value.find(separator);

	if i == -1:
		return ""

	start = i + len(separator)

	return value[start : ]

def between(value, front, back):
	retval = after(value, front)
	retval = before(retval, back)
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
	for match in re.findall(r'[\w_/\.]+\s*=\s*(false|true)', line):
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
"""
unittest {
	import BDD;

	describe("godot_project#parseKeyValues",
		it("Should parse key values", delegate() {
			auto data = `[ext_resource path="res://aaa/bbb.thing965/blah.jpg" singleton = false dot.67.name="res://game.dll" type="Texture" total=8.45 has_space="Bob Smith" is_empty="" id=1]`;
			auto result = parseKeyValues(data);
			auto expected = [
				`type`: `Texture`,
				`path`: `res://aaa/bbb.thing965/blah.jpg`,
				`id`: `1`,
				`total`: `8.45`,
				`has_space`: `Bob Smith`,
				`is_empty`: ``,
				`singleton`: `false`,
				`dot.67.name`: `res://game.dll`
			];
			result.shouldEqual(expected);
		})
	);
}
"""

class HeadingExtResource(object):
	def __init__(self, section):
		self._path = None
		self._type = None
		self._id = -1

	def isValid(self):
		return False

class HeadingConnection(object):
	def __init__(self, section):
		self._signal = None
		self._from = None
		self._to = None
		self._method = None

	def isValid(self):
		return False





class EntryExtResource(object):
	def __init__(self, id):
		self.id = id

class HeadingNode(object):
	def __init__(self, section):
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
							id = int(between(value, "ExtResource(", ")").strip())
							self._instance = EntryExtResource(id)
						case _:
							pass

			# Key value pairs under heading
			# script = ExtResource( 2 )
			if got_heading:
				for key, value in parseKeyValues(line).items():
					match key:
						case "script":
							id = int(between(value, "ExtResource(", ")").strip())
							self._script = EntryExtResource(id)
						case _:
							pass

	def isValid(self):
		return self._name and self._type
'''
unittest {
	import BDD;

	describe("godot_project#HeadingNode",
		it("Should parse node", delegate() {
			auto node = new HeadingNode(
`[node name ="Level" type = "Spatial" parent="." instance= ExtResource( 27 )]
script = ExtResource( 2 )
`);
			node._name.shouldEqual("Level");
			node._type.shouldEqual("Spatial");
			node._parent.shouldEqual(".");
			node._instance.shouldNotBeNull();
			node._instance.id.shouldEqual(27);
			node._script.shouldNotBeNull();
			node._script.id.shouldEqual(2);
		})
	);
}
'''
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

class ProjectFile(object):
	def __init__(self, file_name):
		self._file_name = file_name

class SceneFile(object):
	def __init__(self, file_name):
		self._file_name = file_name
		self._nodes = []
		self._resources = []
		self._connections = []

		for section in readFileSections(file_name):
			#xxx = getSectionType(section)
			#print("<<<<", section, ">>>>", xxx)
			match getSectionType(section):
				case SectionType.Unknown:
					pass
				# [node name="Level" type="Spatial"]
				case SectionType.Node:
					node = HeadingNode(section)
					if node.isValid():
						self._nodes.append(node)
				# [connection signal="area_exited" from="ScreenBox" to="." method="on_screen_box_area_exited"]
				case SectionType.Connection:
					conn = HeadingConnection(section)
					if conn.isValid():
						self._connections.append(conn)
				# [ext_resource path="res://src/ClothHolder/ClothHolder.tscn" type="PackedScene" id=21]
				case SectionType.ExtResource:
					resource = HeadingExtResource(section)
					if resource.isValid():
						self._resources.append(resource)


class GDScriptFile(object):
	def __init__(self, file_name):
		self._file_name = file_name
		self._classes = []
		self._functions = []

		with open(file_name) as f:
			code = f.read()

		parse_tree = parser.parse(code, gather_metadata=True)
		ast = AbstractSyntaxTree(parse_tree)
		#print(ast)


		#print(ast.root_class)
		for c in ast.classes:
			#print(c.lark_node)
			#print(c.name)
			self._classes.append(c.name)
			#print(c.sub_classes)
			for f in c.functions:
				#print(f.name)
				self._functions.append(f.name)


if __name__ == '__main__':
	import os

	project_path = '/home/matt/project/ImmersiveRPG/project/'
	os.chdir(project_path)

	extensions = [".tscn", ".gd", ".godot"]
	entries = []
	for root, dirs, files in os.walk(project_path):
		for name in files:
			entry = os.path.join(root, name)
			ext = os.path.splitext(entry)[-1]
			if not ext in extensions: continue
			if entry.startswith("/home/matt/project/ImmersiveRPG/project/addons/"): continue
			if entry.startswith("/home/matt/project/ImmersiveRPG/project/assets/"): continue
			#print(entry)

			entries.append(entry)

	projects = []
	scenes = []
	scripts = []
	for entry in entries:
		ext = os.path.splitext(entry)[-1]
		match ext:
			case ".godot":
				projects.append(ProjectFile(entry))
			case ".tscn":
				scenes.append(SceneFile(entry))
			case ".gd":
				scripts.append(GDScriptFile(entry))
			case _:
				raise Exception('Unexpected file type: "{0}"'.format(entry))
	'''
	for project in projects:
		print(project._file_name)
	'''
	for scene in scenes:
		print(scene._file_name)
	'''
	for script in scripts:
		print(script._file_name)
		for c in script._classes:
			print("    {0}".format(c))
		for f in script._functions:
			print("    {0}".format(f))
	'''



