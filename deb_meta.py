#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""\
Remote Debian package (.deb) metadata extractor and parser
"""

import io
import logging
import re
import tarfile
from urllib import request

#logging.basicConfig(level='DEBUG')

AR_HEADER = b'!<arch>\n'
DEB_HEADER = b'debian-binary'
DEB_FOOTER = b'`\n2.0\n'
CONTROL_HEADER = b'control.tar.gz'
# More info
# https://www.debian.org/doc/debian-policy/ch-controlfields.html
DEB_MAP = {
    'Package': 'pkgname',
    'Version': 'pkgver',
    'Architecture': 'arch',
    'Maintainer': None,
    'Installed-Size': None,
    'Pre-Depends': 'makedepends',
    'Depends': 'depends',
    'Recommends': 'optdepends',
    'Suggests': 'optdepends',
    'Conflicts': 'conflicts',
    'Replaces': 'replaces',
    'Provides': 'provides',
    'Homepage': 'url',
    'Description': 'pkgdesc',
    'Source': None,
    'Essential': None,
    'Built-Using': None
}


def _get_deb_header(url):
    opener = request.build_opener()
    opener.addheaders = [('Range', 'bytes=0-131')]
    request.install_opener(opener)
    return request.urlopen(url).read()


def _get_control_targz(url, control_length):
    byte_num = 131 + int(control_length)
    opener = request.build_opener()
    opener.addheaders = [('Range', 'bytes=132-{0}'.format(byte_num))]
    request.install_opener(opener)
    return request.urlopen(url).read()


def get_metadata(url):
    """\
    deb package metadata extractor from URL

    :url: .deb package URL
    :returns: 'control' file from a '.deb' archive

    """

    header = _get_deb_header(url)

    if (_is_ar(header) and
        _is_deb(header) and
        _has_control(header)):

        ctrl_meta = _control_meta(header)
        ctrl_targz = _get_control_targz(url, ctrl_meta['size'])
        deb_meta = _extract_control(ctrl_targz)

        # pre-parse metadata
        deb_meta = deb_meta.replace('\n ', ' ')
        return deb_meta

    else:
        return False


def parse_metadata(deb_meta):
    """\
    Metadata parser helper

    :deb_meta: TODO
    :returns: TODO

    """

    deb_parsed = dict()
    for line in deb_meta.splitlines():
        attr = line.partition(': ')
        if not len(attr[0]): continue
        deb_parsed[attr[0]] = attr[2]

    parsed = dict()
    for k, v in DEB_MAP.items():
        if (not v) or (k not in deb_parsed): continue
        parsed[v] = deb_parsed[k]

    return parsed


def _is_ar(header_bytes):

    """\
    GNU ar archive

    Global header (file magic): b'!<arch>\n' 8 bytes

    File header: 60 bytes for
    * filename
    * timestamp
    * owener ID
    * group ID
    * file mode
    * file size
    * file magic (type)
    """

    logging.debug(header_bytes[0:8])
    if header_bytes[0:8] == AR_HEADER:
        logging.info("Archive is an ar archive")
        return True
    else:
        logging.error("Archive is not a valid ar archive")
        return False


def _is_deb(header_bytes):
    logging.debug(header_bytes[8:72])
    if (header_bytes[8:72].startswith(DEB_HEADER)
        and header_bytes[8:72].endswith(DEB_FOOTER)):
        logging.info("Archive is a deb package")
        return True
    else:
        logging.error("Archive is not deb valid deb package")
        return False


def _has_control(header_bytes):
    logging.debug(header_bytes[72:132])
    if header_bytes[72:132].startswith(b'control.tar.gz'):
        logging.info("deb package contains 'control.tar.gz'")
        return True
    else:
        logging.error("deb package does not contain 'control.tar.gz'")
        return False


def _control_meta(header_bytes):
    fields = ['file', 'time', 'uid', 'gid', 'permissions', 'size']
    header_values = header_bytes[72:132].decode().split()[:-1]
    return dict(zip(fields, header_values))


def _extract_control(control_targz):
    io_bytes = io.BytesIO(control_targz)
    ctrl_tar = tarfile.open(fileobj=io_bytes, mode='r:gz')
    return ctrl_tar.extractfile("./control").read().decode()

