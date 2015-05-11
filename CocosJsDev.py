#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: Floyda
# Date: 2015-5-11

import sublime
import sublime_plugin
import os

def get_workdir(file_name):
	path, postfix = os.path.splitext(file_name)
	if postfix != ".js" : return None
	src_dir = path.find("src")
	if src_dir < 0 : return None
	return path[:src_dir]

def check_file(file_name):
	if get_workdir(file_name) is None:
		return False
	return True

def run_local_server(workdir):
	sublime.set_timeout_async(lambda:os.system("%s & cd %s & cocos run -p web & pause" % (workdir[:2], workdir)), 0)


class CocosjsLocalServerCommand(sublime_plugin.WindowCommand):

	def run(self):
		COCOS_CONSOLE_ROOT = os.environ.get('COCOS_CONSOLE_ROOT')
		if COCOS_CONSOLE_ROOT is None:
			sublime.message_dialog("please python COCOS_JS_ROOT/setup.py in cmd")
			return

		view = self.window.active_view()
		file_name = view.file_name()
		if check_file(file_name) is False:
			return
		workdir = get_workdir(file_name)
		run_local_server(workdir)

	def is_enabled(self):
		return True

	def is_visible(self):
		return self.is_enabled()
