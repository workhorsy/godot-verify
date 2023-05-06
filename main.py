#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify

from godot_project_files import *

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
		print(project._path)
	'''
	for scene in scenes:
		print(scene._path)
	'''
	for script in scripts:
		print(script._path)
		for c in script._classes:
			print("    {0}".format(c))
		for f in script._functions:
			print("    {0}".format(f))
	'''



