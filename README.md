# ALSA Mixer WebUI

[![Build Status](https://travis-ci.org/JiriSko/amixer-webui.svg?branch=master)](https://travis-ci.org/JiriSko/amixer-webui)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

Client-server application for easy configuration of ALSA volume controls using network device (smartphone, tablet, PC, etc.).

There exists also [client for Android](https://github.com/JiriSko/amixer-webui-android).

[![Screenshot](docs/screenshot.png)](docs/screenshot.png)


## Server requirements

- python2.6 and newer; or python3.3 and newer
- python-pip as prerequisites for [Flask](http://flask.pocoo.org/) (`pip install flask`)
- alsa-utils
- alsaequal (OPTIONAL: for equalizer)


## Supported browsers

- Internet Explorer
- Edge
- Chrome
- Firefox
- Opera
- Chrome (Android)

## Getting Started

### Download / Clone

You can download [latest release](https://github.com/JiriSko/amixer-webui/releases/latest) as .deb package or source code. Alternatively clone whole repository:

```bash
$ git clone https://github.com/JiriSko/amixer-webui.git
```

## Synopsis

```
alsamixer_webui.py [-p <port=8080>] [-l <host=0.0.0.0>]
```

Script loads configuration file `/etc/amixer-webui.conf` if exists.

## Install on desktop distributions

### For Debian based distributions:

Install [latest](https://github.com/JiriSko/amixer-webui/releases/latest) .deb package and then enable & start amixer service:

```bash
sudo update-rc.d amixer-webui defaults
sudo /etc/init.d/amixer-webui start
```

### Other distributions:

At first install app as root:
```bash
make install
```

And then enable and start amixer-webui service.

----------

Alternatively it can be run from anywhere e.g. in background from `rc.local`.

## Install on OpenWrt

Install app as root using `./openwrt.sh install` command and then enable & start amixer-webui service:

```bash
/etc/init.d/amixer-webui enable
/etc/init.d/amixer-webui start
```

Script automatically restores ALSA settings after reboot.


## License

The application is released under [The MIT License](LICENSE). Software uses [Material Design Lite](https://github.com/google/material-design-lite) library which is licensed under an [Apache-2](https://github.com/google/material-design-lite/blob/master/LICENSE) license.
