#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# File:    alsamixer-webui.py
# Date:    24. 1. 2016
# Author:  Jiri Skorpil <jiri.sko@gmail.com>
# Desc.:   ALSA Mixer WebUI - main application
#

import sys
import os
import socket
import BaseHTTPServer
import SocketServer
import json


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
	static_files = {
		"htm"	: "text/html",
		"html"	: "text/html",
		"jpg"	: "image/jpg",
		"gif"	: "image/gif",
		"png"	: "image/png",
		"svg"	: "image/svg+xml",
		"js"	: "application/javascript",
		"css"	: "text/css",
		"ico"	: "image/x-icon",
		"json"	: "application/json",
		"map"	: "application/json",
	}
	htdocs_root = "htdocs"
	
	server_version = "ALSA Mixer webserver"
	sys_version = ""
	
	def do_GET(self):
		if self.__dynamic_request__("GET") != None or self.__static_files__() != None:
			return
		else:
			self.send_error(404, "File Not Found: %s" % self.path[1:])
	
	def do_PUT(self):
		if self.__dynamic_request__("PUT") == None:
			self.send_error(404, "File Not Found: %s" % self.path[1:])
	
	def __get_channel_name__(self, desc, name, i):
		for control in desc:
			lines = control.split("\n")
			control_name = lines[0].replace("',0", "")[1:]
			if not control_name in name:
				continue;
			
			for line in lines[1:]:
				if name.split(" ")[-2] in line:
					names = line.split(": ")[1].split(" - ")
					return names[i]
		
		return None
	
	def __dynamic_request__(self, mode):
		if (self.path == "/" and mode == "GET"):
			self.send_response(200)
			self.send_header("Conent-Type", "text/html")
			self.end_headers()
			f = open("index.tpl")
			html = f.read().replace("{$hostname}", socket.gethostname())
			f.close()
			self.wfile.write(html)
		
		elif (self.path == "/controls/" and mode == "GET"):
			amixer_chandesc = os.popen("amixer | grep -e control -e channels").read().split("Simple mixer control ")[1:]
			amixer_contents = os.popen("amixer contents").read()
			
			self.send_response(200)
			self.send_header("Conent-Type", "application/json")
			self.end_headers()
			
			interfaces = []
			for i in amixer_contents.split("numid=")[1:]:
				lines = i.split("\n")
				
				interface = {
					"id"		: int(lines[0].split(",")[0]),
					"iface"		: lines[0].split(",")[1].replace("iface=", ""),
					"name"		: lines[0].split(",")[2].replace("name=", "").replace("'", ""),
					"type"		: lines[1].split(",")[0].replace("  ; type=", ""),
					"access"	: lines[1].split(",")[1].replace("access=", ""),
				}
				
				if interface["type"] == "ENUMERATED":
					items = {}
					for line in lines[2:-2]:
						pcs = line.split(" '")
						id = pcs[0].replace("  ; Item #", "")
						name = pcs[1][:-1]
						items[id] = name
					interface["items"] = items
					interface["values"] = []
					for value in lines[-2].replace("  : values=", "").split(","):
						interface["values"].append(int(value))
				
				elif interface["type"] == "BOOLEAN":
					interface["values"] = []
					for value in lines[-2].replace("  : values=", "").split(","):
						interface["values"].append(True if value == "on" else False)
					
				elif interface["type"] == "INTEGER":
					interface["min"] = int(lines[1].split(",")[3].replace("min=", ""))
					interface["max"] = int(lines[1].split(",")[4].replace("max=", ""))
					interface["step"] = int(lines[1].split(",")[5].replace("step=", ""))
					line = ""
					for i in reversed(lines):
						if "  : values=" in i:
							line = i
							break
					interface["values"] = []
					interface["channels"] = []
					i = 0
					for value in line.replace("  : values=", "").split(","):
						interface["values"].append(value)
						channel_desc = self.__get_channel_name__(amixer_chandesc, interface["name"], i)
						if channel_desc != None:
							interface["channels"].append(channel_desc)
						i += 1
					if len(interface["channels"]) != len(interface["values"]):
						interface.pop("channels", None)
				
				interfaces.append(interface)
			
			self.wfile.write(json.dumps(interfaces))
		
		elif (mode == "PUT"):
			path = self.path[1:].split("/")
			
			if path[0] == "control" and path[1].isdigit() and int(path[1]) > 0 and (path[2] == "0" or path[2] == "1"):
				command = "amixer cset numid=%s %s" % (path[1], 'on' if path[2] == '1' else 'off')
				os.popen(command).read()
			
			elif path[0] == "source" and path[1].isdigit() and int(path[1]) > 0 and path[2].isdigit() and int(path[2]) >= 0:
				command = "amixer cset numid=%s %s" % (path[1], path[2])
				os.popen(command).read()
			
			elif path[0] == "volume" and path[1].isdigit() and int(path[1]) > 0:
				volumes = []
				for volume in path[2:]:
					if volume != "" and volume.isdigit():
						volumes.append(volume)
				command = "amixer cset numid=%s %s" % (path[1], ",".join(volumes))
				os.popen(command).read()
			
			else:
				return
			
			self.send_response(200)
			self.send_header("Conent-Type", "text/html")
			self.end_headers()
		
		else:
			return
		
		return True
	
	def __static_files__(self):
		try:
			send_reply = False
			for key in self.static_files:
				if self.path.endswith("." + key):
					mimetype = self.static_files[key]
					send_reply = True
					break
			
			if send_reply == True:
				f = open(os.curdir + os.sep + self.htdocs_root + os.sep + self.path)
				self.send_response(200)
				self.send_header("Content-Type", mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return True
		
		except IOError:
			self.send_error(404, "File Not Found: %s" % self.path[1:])
			return False


if __name__ == "__main__":
	
	port = 8080
	
	if (len(sys.argv) != 1 and len(sys.argv) != 2) or (len(sys.argv) == 2 and sys.argv[1].isdigit() == False):
		print("Usage: %s <port>" % sys.argv[0])
		sys.exit(2)
	elif len(sys.argv) == 2 and sys.argv[1].isdigit():
		port = int(sys.argv[1])
	
	server_address = ("", port)
	
	httpd = SocketServer.TCPServer(server_address, Handler, False) # Do not automatically bind
	httpd.allow_reuse_address = True # Prevent 'Address already in use' on restart
	httpd.server_bind() # Manually bind, to support allow_reuse_address
	httpd.server_activate()
	
	try:
		print("Server is running on port %d" % server_address[1])
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	
	httpd.server_close()
	print("Server stopped")
	
	sys.exit(0)

# end of alsamixer-webui.py
