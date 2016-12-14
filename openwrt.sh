#!/usr/bin/env bash
#
# File:    openwrt.sh
# Date:    12. 12. 2016
# Author:  Jiri Skorpil <jiri.sko@gmail.com>
# Desc.:   Install/uninstall script of amixer-webui for OpenWRT
#

INSTALL_PATH=/usr/share/amixer-webui

case "$1" in
  install)
    mkdir ${INSTALL_PATH}
    cp -r htdocs ${INSTALL_PATH}/
    cp alsamixer_webui.py ${INSTALL_PATH}/
    cp index.tpl ${INSTALL_PATH}/
    cp logo.svg ${INSTALL_PATH}/
    cp README.md ${INSTALL_PATH}/
    cp amixer-webui_openwrt /etc/init.d/amixer-webui
    cp amixer-webui.conf /etc/amixer-webui.conf
    ;;
  uninstall)
    rm -rf ${INSTALL_PATH}
	rm /etc/init.d/amixer-webui
	rm /etc/amixer-webui.conf
    ;;
  *)
    echo "Usage: $0 {install|uninstall}"
    exit 1
    ;;
esac

exit 0
