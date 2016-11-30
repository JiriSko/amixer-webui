#!/usr/bin/env python
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
import json

try:
    # Python 2.x
    PYTHON_VERSION = 2
    import BaseHTTPServer
    import SocketServer
except ImportError:
    # Python 3.x
    PYTHON_VERSION = 3
    from http import server as BaseHTTPServer
    import socketserver as SocketServer

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
        "woff": "font/woff",
        "woff2": "font/woff2",
    }
    htdocs_root = "htdocs"

    server_version = "ALSA Mixer webserver"
    sys_version = ""

    HTTP_OK = 200
    HTTP_NOT_FOUND = 404

    card = None
    equal = False

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
        command = ["amixer"]
        if Handler.card is not None:
            command += ["-c", "%d" % Handler.card]
        if Handler.equal is True:
            command += ["-D", "equal"]
        return command

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

    def __get_controls__(self):
        try:
            amixer = Popen(self.__get_amixer_command__(), stdout=PIPE)
            amixer_channels = Popen(["grep", "-e", "control", "-e", "channels"], stdin=amixer.stdout, stdout=PIPE)
            amixer_chandesc = self.__decode_string(amixer_channels.communicate()[0]).split("Simple mixer control ")[1:]

            amixer_contents = self.__decode_string(Popen(self.__get_amixer_command__() + ["contents"], stdout=PIPE).communicate()[0])
        except OSError:
            return []

        interfaces = []
        for i in amixer_contents.split("numid=")[1:]:
            lines = i.split("\n")

            interface = {
                "id": int(lines[0].split(",")[0]),
                "iface": lines[0].split(",")[1].replace("iface=", ""),
                "name": lines[0].split(",")[2].replace("name=", "").replace("'", ""),
                "type": lines[1].split(",")[0].replace("  ; type=", ""),
                "access": lines[1].split(",")[1].replace("access=", ""),
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

        return interfaces

    def __change_volume(self, num_id, volumes_path):
        volumes = []
        for volume in volumes_path:
            if volume != "" and is_digit(volume):
                volumes.append(volume)
        command = self.__get_amixer_command__() + ["cset", "numid=%s" % num_id, "--", ",".join(volumes)]
        call(command)

    def __dynamic_request__(self, mode):
        if self.path == "/" and mode == "GET":
            """Sends HTML file (GET /)"""
            self.__send_headers("text/html")
            f = open("index.tpl")
            html = f.read().replace("{$hostname}", socket.gethostname())
            f.close()
            self.__write_response(html)

        elif self.path == "/hostname/" and mode == "GET":
            """Sends server's hostname (GET /hostname) [plain text:String]"""
            self.__send_headers("text/plain")
            self.__write_response(socket.gethostname())

        elif self.path == "/cards/" and mode == "GET":
            """Sends list of sound cards (GET /cards) [JSON object - <number:Number>:<name:String>]"""
            self.__send_headers("application/json")

            p1 = Popen(["cat", "/proc/asound/cards"], stdout=PIPE)
            p2 = Popen(["grep", "\]:"], stdin=p1.stdout, stdout=PIPE)
            system_cards = p2.communicate()

            cards = {}
            if p2.returncode == 0:
                for i in self.__decode_string(system_cards[0]).split("\n")[:-1]:
                    card_number = i.split(" [")[0].strip()
                    card_detail = self.__decode_string(Popen(["amixer", "-c", card_number, "info"], stdout=PIPE).communicate()[0])
                    cards[card_number] = card_detail.split("\n")[1].split(":")[1].replace("'", "").strip()

            self.__write_response(json.dumps(cards))

        elif re.match('/card/(\?.*)?', self.path) and mode == "GET":
            """Sends number of selected sound card (GET /card) [JSON - <Number|null>]"""
            self.__send_headers("application/json")
            self.__write_response(json.dumps(Handler.card))

        elif re.match('/controls/(\?.*)?', self.path) and mode == "GET":
            """Sends list of controls of selected sound card (GET /controls/) [JSON - list of objects: {
            --- common keys ---
                access: <String>
                id: <Number>
                iface: <String>
                name: <String>
                type: <ENUMERATED|BOOLEAN|INTEGER:String>
            --- for type ENUMERATED ---
                items: <Object {<number:Number>:<name:String>}>
                values: [<Number> - selected item]
            --- for type BOOLEAN ---
                values: [true|false]
            --- for type INTEGER ---
                channels: <Array of String> - channel names
                min: <Number>
                max: <Number>
                step: <Number>
                values: <Array of Number> - channel values (order corresponds with order in `channels` key)
            }]"""
            self.__send_headers("application/json")
            self.__write_response(json.dumps(self.__get_controls__()))

        elif self.path == "/equalizer/" and mode == "GET":
            """Sends list of equalizer controls (GET /equalizer) [same as /controls/ but contains only controls of INTEGER type]"""
            self.__send_headers("application/json")
            Handler.equal = True
            self.__write_response(json.dumps(self.__get_controls__()))
            Handler.equal = False

        elif mode == "PUT":
            path = self.path[1:].split("/")
            store = True

            try:

                if path[0] == "control" and path[1].isdigit() and int(path[1]) > 0 and (path[2] == "0" or path[2] == "1"):
                    """Turns BOOLEAN control on or off (PUT /control/<control id:integer>/<0|1>/)"""
                    call(self.__get_amixer_command__() + ["cset", "numid=%s" % path[1], "--", 'on' if path[2] == '1' else 'off'])

                elif path[0] == "source" and path[1].isdigit() and int(path[1]) > 0 and path[2].isdigit():
                    """Changes active ENUMERATED item (PUT /source/<control id:integer>/<item number:integer>/)"""
                    call(self.__get_amixer_command__() + ["cset", "numid=%s" % path[1], "--", path[2]])

                elif path[0] == "volume" and path[1].isdigit() and int(path[1]) > 0:
                    """Changes INTEGER channel volumes (PUT /source/<control id:integer>/(<value:number>/)+)"""
                    self.__change_volume(path[1], path[2:])

                elif path[0] == "equalizer" and path[1].isdigit() and int(path[1]) > 0:
                    """Changes equalizer channel values (PUT /equalizer/<control id:integer>/(<value:number>/)+)"""
                    Handler.equal = True
                    card = Handler.card
                    Handler.card = None
                    self.__change_volume(path[1], path[2:])
                    Handler.equal = False
                    Handler.card = card

                elif path[0] == "card" and path[1].isdigit():
                    """Changes selected sound card (PUT /card/<card number:integer>)"""
                    Handler.card = int(path[1])
                    store = False

                else:
                    return

                if store is True:
                    call(["alsactl", "store"])
            except OSError:
                pass

            self.__send_headers("text/html")

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
                f = open(os.curdir + os.sep + self.htdocs_root + os.sep + self.path, 'rb')
                self.__send_headers(mime_type)
                self.wfile.write(f.read())
                f.close()
                return True

        except IOError:
            self.send_error(self.HTTP_NOT_FOUND, "File Not Found: %s" % self.path[1:])
            return False

    def __send_headers(self, content_type, code=HTTP_OK):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def __write_response(self, str):
        self.wfile.write(str if PYTHON_VERSION is 2 else bytes(str, "utf-8"))

    @staticmethod
    def __decode_string(str):
        return str if PYTHON_VERSION is 2 else str.decode("utf-8")


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
