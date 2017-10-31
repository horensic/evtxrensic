# -*- coding: utf-8 -*-
import struct


class MmFile(object):

    def __init__(self, buf, offset):
        self.buf = buf
        self.offset = offset
        self.buf.seek(self.offset)

    def update(self):
        pos = self.buf.tell()
        self.offset = pos

    def correct(self):
        self.buf.seek(self.offset)

    def preview(self):
        pos = self.buf.tell()
        var = ord(self.buf.read(1))
        self.buf.seek(pos)
        return var

    def read_byte(self):
        var = ord(self.buf.read(1))
        self.update()
        return var

    def read_int(self):
        var = struct.unpack('<I', self.buf.read(4))[0]
        self.update()
        return var