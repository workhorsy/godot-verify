#!/usr/bin/env python

# Copyright (c) 2023 Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Verify Godot project using python
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/godot-verify



if __name__ == '__main__':
	from gdtoolkit.parser import parser
	from gdtoolkit.linter.ast import AbstractSyntaxTree

	with open('/home/matt/project/ImmersiveRPG/project/src/Player/Player.gd') as f:
		code = f.read()

	parse_tree = parser.parse(code, gather_metadata=True)
	ast = AbstractSyntaxTree(parse_tree)
	print(ast)


	#print(ast.root_class)
	for c in ast.classes:
		#print(c.lark_node)
		print(c.name)
		#print(c.sub_classes)
		for f in c.functions:
			print(f.name)





