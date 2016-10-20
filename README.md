# ALSA Mixer WebUI

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

Client-server application for easy configuration of ALSA volume controls using network device (smartphone, tablet, PC, etc.).

There exists also [client for Android](https://github.com/JiriSko/amixer-webui-android).

[![Screenshot](screenshot.png)](screenshot.png)


## Server requirements

- python2


## Supported browsers

- Internet Explorer
- Edge
- Chrome
- Firefox
- Opera
- Chrome (Android)

## Getting Started

### Download / Clone

```bash
$ git clone https://github.com/JiriSko/amixer-webui.git
```

Alternatively you can [download](https://github.com/JiriSko/amixer-webui/archive/master.zip) this repository.

## Synopsis

```
alsamixer-webui.py <port=8080>
```

## Install on desktop distributions

You can use init.d script `amixer-webui` (do not forget to set correct [path](https://github.com/JiriSko/amixer-webui/blob/master/amixer-webui#L19) and optionally [port](https://github.com/JiriSko/amixer-webui/blob/master/amixer-webui#L20)):

```bash
sudo cp amixer-webui /etc/init.d/amixer-webui
sudo update-rc.d amixer-webui defaults
sudo /etc/init.d/amixer-webui start
```

or simply run it in background e.g. from `rc.local`.

## Install on OpenWrt

Similarly set correct [path](https://github.com/JiriSko/amixer-webui/blob/master/amixer-webui_openwrt#L14) and [port](https://github.com/JiriSko/amixer-webui/blob/master/amixer-webui_openwrt#L15) and then run:

```bash
cp amixer-webui_openwrt /etc/init.d/amixer-webui
/etc/init.d/amixer-webui enable
/etc/init.d/amixer-webui start
```

Script automatically restores ALSA settings after reboot.


## License

The application is released under [The MIT License](LICENSE). Software uses [Material Design Lite](https://github.com/google/material-design-lite) library which is licensed under an [Apache-2](https://github.com/google/material-design-lite/blob/master/LICENSE) license.
