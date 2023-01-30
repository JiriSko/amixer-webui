#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File:    alsamixer_webui.py
# Date:    24. 1. 2016
# Author:  Jiri Skorpil <jiri.sko@gmail.com>
# Desc.:   ALSA Mixer WebUI - main application
#

import sys
import re
import os
import errno
from subprocess import call, Popen, PIPE
import socket
import json
from flask import Flask, Response
import argparse
try:
    # Python 2.x
    import ConfigParser
except ImportError:
    # Python 3.x
    import configparser as ConfigParser


CONFIG_FILE = '/etc/amixer-webui.conf'
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '8080'


class Handler(Flask):

    card = None
    equal = False

    PULSE_AUDIO_DEVICE_NUMBER = 99999

    def __init__(self, *args, **kwargs):
        Flask.__init__(self, *args, **kwargs)

    def __get_amixer_command__(self):
        command = ["amixer"]
        if self.card == self.PULSE_AUDIO_DEVICE_NUMBER:
            command += ["-D", "pulse"]
        elif self.card is not None:
            command += ["-c", "%d" % self.card]
        if self.equal is True:
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

    def __get_cards__(self):
        system_cards = []
        try:
            with open("/proc/asound/cards", 'rt') as f:
                for l in f.readlines():
                    if ']:' in l:
                        system_cards.append(l.strip())
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise e

        cards = {}
        for i in system_cards:
            card_number = i.split(" [")[0].strip()
            card_detail = Popen(["amixer", "-c", card_number, "info"], stdout=PIPE).communicate()[0]
            cards[card_number] = self.__decode_string(card_detail).split("\n")[1].split(":")[1].replace("'", "").strip()

        pulse = Popen(["amixer", "-D", "pulse", "info"], stdout=PIPE)
        pulse.communicate()
        if pulse.wait() == 0:
            cards[self.PULSE_AUDIO_DEVICE_NUMBER] = "PulseAudio"

        return cards

    def __get_controls__(self):
        try:
            amixer = Popen(self.__get_amixer_command__(), stdout=PIPE)
            amixer_channels = Popen(["grep", "-e", "control", "-e", "channels"], stdin=amixer.stdout, stdout=PIPE)
            amixer_chandesc = self.__decode_string(amixer_channels.communicate()[0]).split("Simple mixer control ")[1:]

            amixer_contents = self.__decode_string(
                Popen(self.__get_amixer_command__() + ["contents"], stdout=PIPE).communicate()[0])
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

    def __get_equalizer__(self):
        self.equal = True
        data = self.__get_controls__()
        self.equal = False
        return data

    def __change_volume__(self, num_id, volumes_path):
        volumes = []
        for volume in volumes_path:
            if volume != "" and is_digit(volume):
                volumes.append(volume)
        command = self.__get_amixer_command__() + ["cset", "numid=%s" % num_id, "--", ",".join(volumes)]
        call(command)

    @staticmethod
    def __decode_string(string):
        return string.decode("utf-8")


def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


app = Handler(__name__, static_folder='htdocs', static_url_path='')


@app.route('/')
def index():
    """Sends HTML file (GET /)"""
    return app.send_static_file('index.html')


@app.route('/hostname/')
def get_hostname():
    """Sends server's hostname [plain text:String]"""
    data = json.dumps(socket.gethostname())
    resp = Response(response=data, status=200, mimetype="application/json")
    return resp


@app.route('/cards/')
def get_cards():
    """Sends list of sound cards [JSON object - <number:Number>:<name:String>]"""
    data = json.dumps(app.__get_cards__())
    resp = Response(response=data, status=200, mimetype="application/json")
    return resp


@app.route('/card/')
def get_card():
    """Sends number of selected sound card [JSON - <Number|null>]"""
    data = json.dumps(app.card)
    resp = Response(response=data, status=200, mimetype="application/json")
    return resp


@app.route('/controls/')
def get_controls():
    """Sends list of controls of selected sound card [JSON - list of objects: {
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
    data = json.dumps(app.__get_controls__())
    resp = Response(response=data, status=200, mimetype="application/json")
    return resp


@app.route('/equalizer/')
def get_equalizer():
    """Sends list of equalizer controls [same as /controls/ but contains only controls of INTEGER type]"""
    data = json.dumps(app.__get_equalizer__())
    resp = Response(response=data, status=200, mimetype="application/json")
    return resp


@app.route('/control/<int:control_id>/<int:status>/', methods=['PUT'])
def put_control(control_id, status):
    """Turns BOOLEAN control on or off"""
    if control_id <= 0:
        return ''
    if status != 0 and status != 1:
        return ''
    call(app.__get_amixer_command__() + ["cset", "numid=%s" % control_id, "--", 'on' if status == 1 else 'off'])
    if os.geteuid() == 0:
        call(["alsactl", "store"])
    return ''


@app.route('/source/<int:control_id>/<int:item>/', methods=['PUT'])
def put_source(control_id, item):
    """Changes active ENUMERATED item"""
    if control_id <= 0:
        return ''
    call(app.__get_amixer_command__() + ["cset", "numid=%s" % control_id, "--", str(item)])
    if os.geteuid() == 0:
        call(["alsactl", "store"])
    return ''


@app.route('/volume/<int:control_id>/<path:volume_path>', methods=['PUT'])
def put_volume(control_id, volume_path):
    """Changes INTEGER channel volumes"""
    app.__change_volume__(control_id, volume_path.split('/'))
    if os.geteuid() == 0:
        call(["alsactl", "store"])
    return ''


@app.route('/equalizer/<int:control_id>/<path:level_path>', methods=['PUT'])
def put_equalizer(control_id, level_path):
    """Changes equalizer channel values"""
    app.equal = True
    card = app.card
    app.card = None
    app.__change_volume__(control_id, level_path.split('/'))
    app.equal = False
    app.card = card
    if os.geteuid() == 0:
        call(["alsactl", "store"])
    return ''


@app.route('/card/<int:card_id>/', methods=['PUT'])
def put_card(card_id):
    """Changes selected sound card"""
    app.card = card_id
    return ''


@app.after_request
def set_server_header(response):
    response.headers["Server"] = "ALSA Mixer webserver"
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--host", type=str)
    parser.add_argument("-p", "--port", type=int)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    if os.path.isfile(CONFIG_FILE):
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE)

        if args.host is None:
            args.host = config.get('amixer-webui', 'host')

        if args.port is None:
            port = config.get('amixer-webui', 'port')
            if is_digit(port):
                args.port = int(port)

    if args.host == "":
        args.host = DEFAULT_HOST

    if args.port is None:
        args.port = DEFAULT_PORT

    try:
        app.run(**vars(args))
    except socket.error as e:
        if e.errno == errno.EPIPE:
            main()
        else:
            raise e

if __name__ == "__main__":

    main()

    sys.exit(0)

# end of alsamixer_webui.py
