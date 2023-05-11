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


def walk_tree_depth_first(node, level = 0):
	from lark import Tree

	is_end = len(node.children) == 1 and not isinstance(node.children[0], Tree)
	yield {'level' : level, 'node' : node, 'is_meta' : False, 'is_end' : not is_end}

	is_end = len(node.children) == 1 and not isinstance(node.children[0], Tree)
	if is_end:
		yield {'level' : 0, 'node' : node.children[0], 'is_meta' : True, 'is_end' : is_end}
		return

	for child in node.children:
		if isinstance(child, Tree):
			yield from walk_tree_depth_first(child, level+1)
		else:
			is_end = True
			yield {'level' : (level+1), 'node' : child, 'is_meta' : False, 'is_end' : is_end}

class GDScriptFile(object):
	def __init__(self, file_name, leaf_visitor_cb):
		import sys
		from lark import Tree
		from lark.lexer import Token

		self._path = file_name
		self._classes = []
		self._functions = []

		with open(file_name) as f:
			code = f.read()

		print("*" * 80)
		parse_tree = parser.parse(code, gather_metadata=True)
		#print(parse_tree.pretty())

		for entry in walk_tree_depth_first(parse_tree):
			end = "\n" if entry["is_end"] else ""
			start = "\t" if entry["is_meta"] else ""
			indent = entry["level"] * "    "
			node = entry["node"]
			if isinstance(node, Tree):
				data = node.data
				sys.stdout.write(f'{indent}{start}{data}{end}')
			elif isinstance(node, Token):
				name = node.type
				value = node.value
				sys.stdout.write(f'{indent}{start}{name}:{value}{end}')
			else:
				print("Unexpected node type: {0}".format(type(node)))

		'''
		for x in parse_tree.iter_subtrees():#iter_subtrees_topdown():
			print("!!!!: ", x)
		'''
		print("*" * 80)
		#ast = AbstractSyntaxTree(parse_tree)
		#print(ast)
		#print("*" * 80)
		#import pprint
		#pp = pprint.PrettyPrinter(indent=4)
		#pp.pprint(parse_tree.__dict__)
		#print(parse_tree)
		#print("*" * 80)

		import lark
		'''
		print("*" * 80)
		next_children = [[parse_tree]]
		while len(next_children) > 0:
			children = next_children.pop(0)
			parent = children.pop(0)

			#leaf_visitor_cb(entry)

			if isinstance(parent, lark.lexer.Token):
				print("    Token: ", parent)
				#entries.append(child)
			elif isinstance(parent, lark.tree.Tree):
				print("Tree: ", parent.data)

				#parent = entry
				while len(parent.children) > 0:
					children = parent.children.copy()
					parent = children.pop(0)
					if len(children) > 0:
						next_children.insert(0, children)

			else:
				print("@@@ unexpected: ", entry)
		print("*" * 80)
		'''
		#print(ast.root_class)
		#self._ast = ast
		#self._root_class = ast.root_class.name

		#print("!!! lark_node", ast.root_class.lark_node)
		#print("!!! name", ast.root_class.name)
		#print("!!! sub_classes", ast.root_class.sub_classes)
		'''
		for f in ast.root_class.functions:
			print("!!! function", f.name)

		for c in ast.classes:
			#print(c.lark_node)
			#print(c.name)
			self._classes.append(c.name)
			#print(c.sub_classes)
			for f in c.functions:
				#print(f.name)
				self._functions.append(f.name)
		'''
