#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify

import unittest
from godot_verify import *

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

if __name__ == '__main__':
	unittest.main()
