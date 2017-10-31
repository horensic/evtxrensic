# -*- coding: utf-8 -*-

from zlib import crc32
import mmap
from .defines import *
from .view import *
from BinXML.binxml import BinXML
from Util.MmFile import MmFile
from Util.Error import *


# import cgitb
# cgitb.enable(format='text')


class Evtx(object):

    def __init__(self, fp):
        self.filePath = fp
        self.fileHeader = None

    def __enter__(self):
        self.evtxFile = open(unicode(self.filePath), 'rb')
        self.buf = mmap.mmap(self.evtxFile.fileno(), 0, access=mmap.ACCESS_READ)
        self.fileHeader = EvtxFileHeader(self.buf, 0x0)
        return self

    def __exit__(self, type, value, traceback):
        self.evtxFile.close()
        self.buf = None
        self.fileHeader = None

    def __repr__(self):
        return 'EVTX File'

    def chunks(self):
        for chunk in self.fileHeader.chunks():
            yield chunk

    def records(self):
        for chunk in self.fileHeader.chunks():
            for record in chunk.records():
                yield record


class EvtxFileHeader(MmFile):

    def __init__(self, buf, offset):
        super(EvtxFileHeader, self).__init__(buf, offset)
        fhdr = self.buf.read(EVTX_HDR_SZ)
        fields = dict(zip(EVTX_HDR_FIELDS, struct.unpack(EVTX_HDR_FORMAT, fhdr)))
        for key in fields:
            setattr(self, key, fields[key])

    def __repr__(self):
        return 'EVTX File Header'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def check_signature(self):
        return getattr(self, 'signature') == EVTX_HDR_SIGNATURE

    def check_error(self):
        pass

    def chunks(self):
        ofs = self.offset + getattr(self, 'header_block_size')
        while ofs + 0x10000 <= len(self.buf):
            try:
                yield EvtxChunk(self.buf, ofs)
            except InvalidChunkException as e:
                # 나중에 청크 외 데이터 추출해주는 옵션에서 사용하면 될 듯.
                print(e)
            ofs += 0x10000


class EvtxChunk(MmFile):

    def __init__(self, buf, offset):
        super(EvtxChunk, self).__init__(buf, offset)
        self.start = self.offset
        chnkhdr = self.buf.read(EVTX_CHNK_HDR_SZ)
        fields = dict(zip(EVTX_CHNK_HDR_FIELDS, struct.unpack(EVTX_CHNK_HDR_FORMAT, chnkhdr)))
        for key in fields:
            setattr(self, key, fields[key])
        self.templateTable = dict()
        self.stringTable = dict()

        if not self.check_signature():
            raise InvalidChunkException

        self.strings()
        self.templates()


    def __repr__(self):
        return 'EVTX Chunk'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def check_signature(self):
        return getattr(self, 'signature') == EVTX_CHNK_HDR_SIGNATURE

    def check_error(self):
        pass

    def template_id_preview(self, offset):
        try:
            self.buf.seek(offset - 8)
        except ValueError as e:
            print(self.buf.tell(), self.offset)
            exit(-1)
        return self.read_int()

    def strings(self):
        start = self.start + EVTX_CHNK_HDR_SZ
        for i in range(EVTX_CHNK_STRT_SZ / 4):
            ofs = start + i * 4
            self.buf.seek(ofs)
            str_id = self.read_int()
            if str_id > 0:
                str_ofs = self.start + str_id
                self.stringTable[str_id] = str_ofs

    def templates(self):
        start = self.start + EVTX_CHNK_HDR_SZ + EVTX_CHNK_STRT_SZ
        for i in range(EVTX_CHNK_TPL_SZ / 4):
            ofs = start + i * 4
            self.buf.seek(ofs)
            tpl_ofs = self.read_int()
            if tpl_ofs > 0:
                offset = self.start + tpl_ofs
                tpl_id = self.template_id_preview(offset)
                self.templateTable[tpl_ofs] = {tpl_id: offset}

    def records(self):
        ofs = self.start + 0x200
        record = EvtRecord(self.buf, ofs, self)
        freeSpaceOffset = getattr(self, 'free_space_offset')

        while (record.offset < self.start + freeSpaceOffset) and (record.record_size() > 0):
            yield record
            try:
                record = EvtRecord(self.buf, record.offset + record.record_size(), self)
            except InvalidRecordException:
                return


class EvtRecord(MmFile):

    def __init__(self, buf, offset, chunk):
        super(EvtRecord, self).__init__(buf, offset)
        self.templateTable = chunk.templateTable
        self.stringTable = chunk.stringTable
        rcdHdr = self.buf.read(RECORD_HDR_SZ)
        fields = dict(zip(RECORD_HDR_FIELDS, struct.unpack(RECORD_HDR_FORMAT, rcdHdr)))
        for key in fields:
            setattr(self, key, fields[key])

        if not self.check_signature():
            raise InvalidRecordException

    def __repr__(self):
        return 'Event Record'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def check_signature(self):
        return getattr(self, 'signature') == RECORD_HDR_SIGNATURE

    def record_size(self):
        return getattr(self, 'size')

    def read_xml(self):
        xmlSize = self.record_size() - RECORD_HDR_SZ
        ofs = self.offset + RECORD_HDR_SZ  # point to fragment header
        event = BinXML(self.buf, ofs, xmlSize, self.templateTable, self.stringTable)
        event.print_xml()

    def get_xml(self):
        xmlSize = self.record_size() - RECORD_HDR_SZ
        ofs = self.offset + RECORD_HDR_SZ  # point to fragment header
        event = BinXML(self.buf, ofs, xmlSize, self.templateTable, self.stringTable)
        rv = RecordView(event.root)
        # rv.get_element()
        # rv.get_message()
        return rv
