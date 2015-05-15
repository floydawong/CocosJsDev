
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Floyda

import sublime
import sublime_plugin
import os
import sys
import webbrowser
import threading
from threading import Thread
try:
	from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
	import BaseHTTPServer
	from SimpleHTTPServer import SimpleHTTPRequestHandler


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



class CocosjsLocalServerCommand(sublime_plugin.WindowCommand):
	def __init__(self, window):
		super(CocosjsLocalServerCommand, self).__init__(window)
		self.cur_server_port = None
		self.cur_workdir = None
		self._host = '127.0.0.1'
		self._port = 8000
		self._port_max_add = 2000
		self.cocos_console_root = _find_environment_variable("COCOS_CONSOLE_ROOT")
		# sublime.set_timeout_async(lambda:os.system('ps x|grep cocos2d-js|xargs kill -9'), 0)
		# os.system('ps x|grep cocos2d-js|xargs kill -9')

	def get_free_port(self):
		HandlerClass = BaseHTTPRequestHandler
		ServerClass  = HTTPServer
		Protocol     = "HTTP/1.0"
		HandlerClass.protocol_version = Protocol

		host = self._host
		port = self._port
		port_max_add = self._port_max_add
		delta = 0

		while (delta <= port_max_add):
		    port += 1
		    delta += 1
		    server_address = (host, port)
		    try:
		        httpd = ServerClass(server_address, HandlerClass)
		    except Exception as e:
		        httpd = None

		    if httpd is not None:
		        break

		if httpd is None:
			sublime.message_dialog("Start server failed.")
			return None

		return port

	def run_web(self, workdir):
		self.cur_workdir = workdir
		self.cur_server_port = self.get_free_port()

		if _isWindows(): 
			sublime.set_timeout_async(lambda:os.system("%s & cd %s & cocos run -p web & pause" % (workdir[:2], workdir)), 0)
		if _is_mac(): 
			# os.system('ps x|grep cocos2d-js|xargs kill -9')
			sublime.status_message('Cocos2d-js Local Server is Starting . . .')
			sublime.set_timeout_async(lambda:os.system("%s/cocos run -s %s -p web --port %s" % (self.cocos_console_root, workdir, self.cur_server_port)), 0)
		if _isLinux():
			pass

	def run_webbrowser(self, workdir):
		if self.cur_workdir != workdir:
			self.run_web(workdir)
			return

		port = self.cur_server_port
		url = 'http://%s:%s' % (self._host, port)
		webbrowser.open_new(url)
		sublime.status_message('open webbrowser : %s' % url)

	def run(self):
		if self.cocos_console_root == None:
			sublime.message_dialog("Install Cocos2d-js by %COCOS_JS_ROOT%/setup.py")
			return

		workdir = get_workdir(self.window.active_view().file_name())
		if workdir == None: return

		self.run_webbrowser(workdir)


	def is_enabled(self):
		return True

	def is_visible(self):
		return self.is_enabled()




		
