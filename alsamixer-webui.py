#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# File:    alsamixer-webui.py
# Date:    24. 1. 2016
# Author:  Jiri Skorpil <jiri.sko@gmail.com>
# Desc.:   ALSA Mixer WebUI - main application
#

import sys
import re
import os
from subprocess import call, Popen, PIPE
import socket
import BaseHTTPServer
import SocketServer
import json


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    static_files = {
        "htm": "text/html",
        "html": "text/html",
        "jpg": "image/jpg",
        "gif": "image/gif",
        "png": "image/png",
        "svg": "image/svg+xml",
        "js": "application/javascript",
        "css": "text/css",
        "ico": "image/x-icon",
        "json": "application/json",
        "map": "application/json",
    }
    htdocs_root = "htdocs"

    server_version = "ALSA Mixer webserver"
    sys_version = ""

    HTTP_OK = 200
    HTTP_NOT_FOUND = 404

    card = None

    def do_GET(self):
        if self.__dynamic_request__("GET") is not None or self.__static_files__() is not None:
            return
        else:
            self.send_error(self.HTTP_NOT_FOUND, "File Not Found: %s" % self.path[1:])

    def do_PUT(self):
        if self.__dynamic_request__("PUT") is None:
            self.send_error(self.HTTP_NOT_FOUND, "File Not Found: %s" % self.path[1:])

    @staticmethod
    def __get_amixer_command__():
        if Handler.card is None:
            return ["amixer"]
        else:
            return ["amixer", "-c", "%d" % Handler.card]

    @staticmethod
    def __get_channel_name__(desc, name, i):
        for control in desc:
            lines = control.split("\n")
            control_name = re.sub("',[0-9]+", "", lines[0][1:])
            if control_name not in name:
                continue

            for line in lines[1:]:
                if name.split(" ")[-2] in line:
                    names = line.split(": ")[1].split(" - ")
                    return names[i]

        return None

    def __dynamic_request__(self, mode):
        if self.path == "/" and mode == "GET":
            self.send_response(self.HTTP_OK)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            f = open("index.tpl")
            html = f.read().replace("{$hostname}", socket.gethostname())
            f.close()
            self.wfile.write(html)

        elif self.path == "/hostname/" and mode == "GET":
            self.send_response(self.HTTP_OK)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()

            self.wfile.write(socket.gethostname())

        elif self.path == "/cards/" and mode == "GET":
            self.send_response(self.HTTP_OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            p1 = Popen(["cat", "/proc/asound/cards"], stdout=PIPE)
            p2 = Popen(["grep", "\]:"], stdin=p1.stdout, stdout=PIPE)
            system_cards = p2.communicate()

            cards = {}
            if p2.returncode == 0:
                for i in system_cards[0].split("\n")[:-1]:
                    card_number = i.split(" [")[0].strip()
                    card_detail = Popen(["amixer", "-c", card_number, "info"], stdout=PIPE).communicate()[0]
                    cards[card_number] = card_detail.split("\n")[1].split(":")[1].replace("'", "").strip()

            self.wfile.write(json.dumps(cards))

        elif self.path == '/card/' and mode == "GET":
            self.send_response(self.HTTP_OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(Handler.card))

        elif self.path == "/controls/" and mode == "GET":
            amixer = Popen(self.__get_amixer_command__(), stdout=PIPE)
            amixer_channels = Popen(["grep", "-e", "control", "-e", "channels"], stdin=amixer.stdout, stdout=PIPE)
            amixer_chandesc = amixer_channels.communicate()[0].split("Simple mixer control ")[1:]

            amixer_contents = Popen(self.__get_amixer_command__() + ["contents"], stdout=PIPE).communicate()[0]

            self.send_response(self.HTTP_OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            interfaces = []
            for i in amixer_contents.split("numid=")[1:]:
                lines = i.split("\n")

                interface = {
                    "id":       int(lines[0].split(",")[0]),
                    "iface":    lines[0].split(",")[1].replace("iface=", ""),
                    "name":     lines[0].split(",")[2].replace("name=", "").replace("'", ""),
                    "type":     lines[1].split(",")[0].replace("  ; type=", ""),
                    "access":   lines[1].split(",")[1].replace("access=", ""),
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
                    for j in reversed(lines):
                        if "  : values=" in j:
                            line = j
                            break
                    interface["values"] = []
                    interface["channels"] = []
                    i = 0
                    for value in line.replace("  : values=", "").split(","):
                        interface["values"].append(value)
                        channel_desc = self.__get_channel_name__(amixer_chandesc, interface["name"], i)
                        if channel_desc is not None:
                            interface["channels"].append(channel_desc)
                        i += 1
                    if len(interface["channels"]) != len(interface["values"]):
                        interface.pop("channels", None)

                interfaces.append(interface)

            self.wfile.write(json.dumps(interfaces))

        elif mode == "PUT":
            path = self.path[1:].split("/")

            if path[0] == "control" and path[1].isdigit() and int(path[1]) > 0 and (path[2] == "0" or path[2] == "1"):
                call(self.__get_amixer_command__() + ["cset", "numid=%s" % path[1], "--", 'on' if path[2] == '1' else 'off'])

            elif path[0] == "source" and path[1].isdigit() and int(path[1]) > 0 and path[2].isdigit():
                call(self.__get_amixer_command__() + ["cset", "numid=%s" % path[1], "--", path[2]])

            elif path[0] == "volume" and path[1].isdigit() and int(path[1]) > 0:
                volumes = []
                for volume in path[2:]:
                    if volume != "" and is_digit(volume):
                        volumes.append(volume)
                command = self.__get_amixer_command__() + ["cset", "numid=%s" % path[1], "--", ",".join(volumes)]
                call(command)

            elif path[0] == "card" and path[1].isdigit():
                Handler.card = int(path[1])

            else:
                return

            call(["alsactl", "store"])

            self.send_response(self.HTTP_OK)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

        else:
            return

        return True

    def __static_files__(self):
        try:
            mime_type = None
            for key in self.static_files:
                if self.path.endswith("." + key):
                    mime_type = self.static_files[key]
                    break

            if mime_type is not None:
                f = open(os.curdir + os.sep + self.htdocs_root + os.sep + self.path)
                self.send_response(self.HTTP_OK)
                self.send_header("Content-Type", mime_type)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return True

        except IOError:
            self.send_error(self.HTTP_NOT_FOUND, "File Not Found: %s" % self.path[1:])
            return False


def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


if __name__ == "__main__":

    port = 8080

    if (len(sys.argv) != 1 and len(sys.argv) != 2) or (len(sys.argv) == 2 and not sys.argv[1].isdigit()):
        print("Usage: %s <port>" % sys.argv[0])
        sys.exit(2)
    elif len(sys.argv) == 2 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    server_address = ("", port)

    httpd = SocketServer.TCPServer(server_address, Handler, False)  # Do not automatically bind
    httpd.allow_reuse_address = True  # Prevent 'Address already in use' on restart
    httpd.server_bind()  # Manually bind, to support allow_reuse_address
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
