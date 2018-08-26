#
# File:    Makefile
# Date:    12. 12. 2016
# Author:  Jiri Skorpil <jiri.sko@gmail.com>
# Desc.:   Makefile for ALSA Mixer WebUI
#

INSTALL_PATH=/usr/share/amixer-webui
BUILD_PATH=production/deb-package

VERSION := $(shell git describe --tags | cut -c2- > .version && cat .version)

.PHONY: all
all:

.PHONY: install
install: clean package
	mkdir ${INSTALL_PATH}
	rsync -av --progress ${BUILD_PATH}/ / --exclude DEBIAN
	cp amixer-webui.conf /etc/amixer-webui.conf
	cp amixer-webui /etc/init.d/amixer-webui

.PHONY: uninstall
uninstall:
	rm -rf ${INSTALL_PATH}
	rm /etc/init.d/amixer-webui
	rm /etc/amixer-webui.conf

.PHONE: package
package:
	mkdir -p ${BUILD_PATH}${INSTALL_PATH}
	cp -r htdocs ${BUILD_PATH}${INSTALL_PATH}/
	cp .version ${BUILD_PATH}${INSTALL_PATH}/
	cp alsamixer_webui.py ${BUILD_PATH}${INSTALL_PATH}/
	cp amixer-webui ${BUILD_PATH}${INSTALL_PATH}/
	cp amixer-webui.conf ${BUILD_PATH}${INSTALL_PATH}/
	cp logo.svg ${BUILD_PATH}${INSTALL_PATH}/
	cp README.md ${BUILD_PATH}${INSTALL_PATH}/

.PHONY: deb
deb: package
	touch ${BUILD_PATH}/DEBIAN/md5sums
	cd ${BUILD_PATH} && find * ! -path "DEBIAN/*" -type f -exec md5sum {} \; >> DEBIAN/md5sums
	sed "s/VERSION/${VERSION}/g" production/DEBIAN-control > ${BUILD_PATH}/DEBIAN/control
	du -sx --apparent-size --exclude ${BUILD_PATH}/DEBIAN ${BUILD_PATH} | awk '{ print "Installed-Size: " $$1 }' >> ${BUILD_PATH}/DEBIAN/control
	fakeroot dpkg-deb -b production/deb-package production/amixer-webui_${VERSION}_all.deb

.PHONY: clean
clean:
	rm -rf ${BUILD_PATH}/usr ${BUILD_PATH}/DEBIAN/control ${BUILD_PATH}/DEBIAN/md5sums
