#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify


from godot_project_files_parser import *

class ProjectFile(object):
	def __init__(self, file_name):
		import os
		import helpers

		self._path = file_name
		self._main_scene_path = None
		self._error = None

		# Read the project.godot file to find the main .tscn
		if not os.path.exists(file_name):
			self._error = "Failed to find {0} file ...".format(file_name)
			return

		for section in readFileSections(file_name):
			data = parseAllSectionKeyValues(section)
			# [application]
			# run/main_scene="res://src/Level/Level.tscn"
			heading = data.get("[application]", None)
			if heading:
				entry = heading.get("run/main_scene", None)
				if entry:
					self._main_scene_path = helpers.after(entry, 'res://')

class SceneFile(object):
	def __init__(self, file_name):
		import os

		self._path = file_name
		self._error = None
		self._nodes = []
		self._resources = []
		self._connections = []

		if not os.path.exists(file_name):
			self._error = "Failed to find {0} file ...".format(file_name)
			return


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
		self._path = file_name
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
