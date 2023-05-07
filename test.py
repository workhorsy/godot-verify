#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify

import unittest
from godot_project_files import *

_root_path = ""
def setPath(project_path):
	import os
	global _root_path
	if not _root_path:
		_root_path = os.getcwd()

	os.chdir(os.path.join(_root_path, project_path))

def resetPath():
	import os
	global _root_path
	os.chdir(_root_path)

class TestParseKeyValues(unittest.TestCase):
	def test_call(self):
		data = '[ext_resource path="res://aaa/bbb.thing965/blah.jpg" singleton = false dot.67.name="res://game.dll" type="Texture" total=8.45 has_space="Bob Smith" is_empty="" id=1]'
		result = parseKeyValues(data)
		expected = {
			'type': 'Texture',
			'path': 'res://aaa/bbb.thing965/blah.jpg',
			'id': '1',
			'total': '8.45',
			'has_space': 'Bob Smith',
			'is_empty': '',
			'singleton': 'false',
			'dot.67.name': 'res://game.dll'
		}
		self.assertEqual(result, expected)

class TestHeadingNode(unittest.TestCase):
	def test_call(self):
		data = '''[node name ="Level" type = "Spatial" parent="." instance= ExtResource( 27 )]
script = ExtResource( 2 )
'''

		node = HeadingNode(data)
		self.assertEqual(node._name, "Level")
		self.assertEqual(node._type, "Spatial")
		self.assertEqual(node._parent, ".")
		self.assertIsNotNone(node._instance)
		self.assertEqual(node._instance.id, 27)
		self.assertIsNotNone(node._script)
		self.assertEqual(node._script.id, 2)

class TestHeadingConnection(unittest.TestCase):
	def test_call(self):
		data = '''[connection signal="pressed" from="Button" to="." method="on_button_pressed"]
'''
		conn = HeadingConnection(data)

		self.assertEqual(conn._signal, "pressed")
		self.assertEqual(conn._from, "Button")
		self.assertEqual(conn._to, ".")
		self.assertEqual(conn._method, "on_button_pressed")

class TestHeadingExtResource(unittest.TestCase):
	def test_call(self):
		data = '[ext_resource path="res://src/ClothHolder/ClothHolder.tscn" type="PackedScene" id=21]'
		resource = HeadingExtResource(data)

		self.assertEqual(resource._path, "src/ClothHolder/ClothHolder.tscn")
		self.assertEqual(resource._type, "PackedScene")
		self.assertEqual(resource._id, 21)

class TestHeadingSceneFile(unittest.TestCase):
	def setUp(self):
		setPath("test_projects/project_normal/project/")

	def tearDown(self):
		resetPath()

	def test_should_parse_scene_with_child_scene(self):
		scene = SceneFile("Level/Level.tscn")
		self.assertEqual(scene._path, "Level/Level.tscn")
		self.assertIsNone(scene._error)
		self.assertEqual(len(scene._resources), 2)

		self.assertEqual(scene._resources[0]._type, "PackedScene")
		self.assertEqual(scene._resources[0]._path, "Player/Player.tscn")
		self.assertEqual(scene._resources[0].isValid(), True)

		self.assertEqual(scene._resources[1]._type, "PackedScene")
		self.assertEqual(scene._resources[1]._path, "Box2/Box2.tscn")
		self.assertEqual(scene._resources[1].isValid(), True)

	def test_should_parse_scene_with_child_resources(self):
		scene = SceneFile("Player/Player.tscn")
		self.assertEqual(scene._path, "Player/Player.tscn")
		self.assertIsNone(scene._error)
		self.assertEqual(len(scene._resources), 2)

		self.assertEqual(scene._resources[0]._type, "Texture")
		self.assertEqual(scene._resources[0]._path, "icon.png")
		self.assertEqual(scene._resources[0].isValid(), True)

		self.assertEqual(scene._resources[1]._type, "Script")
		self.assertEqual(scene._resources[1]._path, "Player/Player.gd")
		self.assertEqual(scene._resources[1].isValid(), True)

	def test_should_fail_to_parse_invalid_scene(self):
		scene = SceneFile("Level/XXX.tscn")
		self.assertEqual(scene._path, "Level/XXX.tscn")
		self.assertIsNotNone(scene._error)
		self.assertEqual(scene._error, "Failed to find Level/XXX.tscn file ...")
		self.assertEqual(len(scene._resources), 0)


class TestProjectFile(unittest.TestCase):
	def setUp(self):
		setPath("test_projects/project_normal/project/")

	def tearDown(self):
		resetPath()

	def test_should_parse_project(self):
		project = ProjectFile("project.godot")
		self.assertEqual(project._path, "project.godot")
		self.assertEqual(project._main_scene_path, "Level/Level.tscn")
		self.assertIsNone(project._error)

	def test_should_fail_to_parse_invalid_project(self):
		project = ProjectFile("XXX.godot")
		self.assertEqual(project._path, "XXX.godot")
		self.assertIsNone(project._main_scene_path)
		self.assertIsNotNone(project._error)
		self.assertEqual(project._error, "Failed to find XXX.godot file ...")

class TestGDScriptFile(unittest.TestCase):
	def setUp(self):
		setPath("test_projects/project_normal/project/")

	def tearDown(self):
		resetPath()

	def test_default(self):
		gdscript = GDScriptFile("Player/Player.gd", lambda x: x)
		#import json
		#print("!!!!!!!", json.dumps(gdscript.__dict__))
		#print(gdscript._classes)
		#print(gdscript._functions)

		self.assertEqual(gdscript._path, "Player/Player.gd")
		self.assertEqual(gdscript._classes, ["FIXME"])
		self.assertEqual(gdscript._functions, ["FIXME"])

if __name__ == '__main__':
	unittest.main()
