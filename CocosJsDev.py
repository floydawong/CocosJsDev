#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: Floyda
# Date: 2015-5-11

import sublime
import sublime_plugin
import os
import sys


MAC_CHECK_FILES   = ['.bash_profile', '.bash_login', '.profile']
LINUX_CHECK_FILES = ['.bashrc']
ZSH_CHECK_FILES   = ['.zshrc']
RE_FORMAT         = r'^export[ \t]+%s=(.+)'


def _isWindows():
	return sys.platform == 'win32'

def _isLinux():
	return sys.platform.startswith('linux')

def _is_mac():
	return sys.platform == 'darwin'

def _is_zsh():
	shellItem = os.environ.get('SHELL')
	if shellItem is not None:
		if len(shellItem) >= 3:
			return shellItem[-3:] == "zsh"
	return False

def _get_unix_file_list():
	file_list = None
	if _is_zsh():
		file_list = ZSH_CHECK_FILES
	elif _isLinux():
		file_list = LINUX_CHECK_FILES
	elif _is_mac():
		file_list = MAC_CHECK_FILES
	return file_list

def _search_unix_variable(var_name, file_name):
	if not os.path.isfile(file_name):
		return None

	import re
	str_re = RE_FORMAT % var_name
	patten = re.compile(str_re)
	ret = None

	for line in open(file_name , encoding='utf-8'):
		str1  = line.lstrip(' \t')
		match = patten.match(str1)
		if match is not None:
			ret = match.group(1)

	return ret

def _find_environment_variable(var):
	ret = os.getenv(var)
	if ret == None:
		if not _isWindows():
			file_list = _get_unix_file_list()

			if file_list is not None:
				home = os.path.expanduser('~')
				for name in file_list:
					path = os.path.join(home, name)
					ret  = _search_unix_variable(var, path)
					if ret is not None:
						break

	return ret

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

def run_local_server(file_name):
	COCOS_CONSOLE_ROOT = _find_environment_variable("COCOS_CONSOLE_ROOT")
	if COCOS_CONSOLE_ROOT == None:
		sublime.message_dialog("Install Cocos2d-js by %COCOS_JS_ROOT%/setup.py")
		return

	WORKDIR = get_workdir(file_name)
	if WORKDIR == None: return

	def _Mac():
		os.system("ps x| grep cocos2d-js | xargs kill -9")
		os.system("%s/cocos run -s %s -p web --port 8000" % (COCOS_CONSOLE_ROOT, WORKDIR))
		os.system('open "http://127.0.0.1:8000"')

	if _isWindows(): 
		sublime.set_timeout_async(lambda:os.system("%s & cd %s & cocos run -p web & pause" % (WORKDIR[:2], WORKDIR)), 0)
	if _is_mac(): 
		sublime.set_timeout_async(_Mac, 0)
	if _isLinux():
		pass



class CocosjsLocalServerCommand(sublime_plugin.WindowCommand):
	def run(self):
		print("run_command: cocosjs_local_server")
		run_local_server(self.window.active_view().file_name())

	def is_enabled(self):
		return True

	def is_visible(self):
		return self.is_enabled()

