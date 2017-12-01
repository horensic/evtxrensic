# -*- coding: utf-8 -*-

from xml.etree.ElementTree import Element, dump
from Util.MmFile import MmFile
from Util.Error import *
from defines import *
from types import *


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class BinXML(MmFile):

    def __init__(self, buf, offset, size, templateT, stringT):
        super(BinXML, self).__init__(buf, offset)
        self.size = size
        self.templateTable = templateT
        self.stringTable = stringT
        for k, v in self.stringTable.items():
            self.chunk_start = v - k
            break
        self.start_sarray = int()
        self.templateSize = int()
        self.sArray = list()
        self.read_template()
        self.root = self.tokenizer()

    def __repr__(self):
        return "BinXML(Size={})".format(self.size)

    def tokenizer(self):
        stack = list()
        root = None
        # stage 0
        ofs = self.offset
        # stack init routine
        stack.append('I')
        # stage 1
        while (self.offset - ofs) <= self.templateSize:
            # print(self.buf.tell(), self.offset)
            tid = self.read_byte()
            # print(self.buf.tell(), self.offset)
            token = Token(self.buf, self.offset, tid, self.stringTable, self.sArray)
            if token.EOF:
                return root
            # stage 2
            if stack[-1] is 'I':
                stack.pop()
                root, child = self.make_element(token)
                if child:
                    stack.append('R')
                else:
                    return root

            elif stack[-1] is 'R':
                if token.end:
                    stack.pop()
                else:
                    tmp, child = self.make_element(token)
                    if child:
                        stack.pop()
                        stack.append(tmp)
                    root.append(tmp)

            else:
                if token.end:
                    stack.pop()
                    stack.append('R')
                else:
                    tmp, child = self.make_element(token)
                    preElem = stack.pop()
                    preElem.append(tmp)
                    if child:
                        stack.append(preElem)
                        stack.append(tmp)

                    stack.append(preElem)
        return root

    def make_element(self, t):
        token = t
        children = None
        elem = Element(token.name)

        if not token.attrib:
            pass
        else:
            for a, v in zip(token.attrib, token.value):
                if v is not "NULL":
                    elem.attrib[a] = v

        if (token.content is None) and not isinstance(token.content, Element):
            elem.text = None
            if not token.empty:
                children = True
        else:
            if isinstance(token.content, Element):
                if token.name == u"SubRoot":
                    elem = token.content
                else:
                    elem.append(token.content)
            else:
                elem.text = token.content

        return elem, children

    def read_template(self):
        # 첫 번째 fragment 헤더는 있을 수도 있고, 없을 수도 있고!
        tid = self.read_byte()
        if TOKEN_LOOKUP_TABLE[tid] is 'FragmentHeader':
            FragmentHeader(self.buf, self.offset)
            self.update()
            tid = self.read_byte()

        if TOKEN_LOOKUP_TABLE[tid] is 'TemplateInstance':
            templateIst = TemplateInstance(self.buf, self.offset)
            tpl_id = templateIst.template_id
            tpl_offset = templateIst.def_data_offset()
            self.update()
            ra = self.buf.tell()

            if tpl_offset not in self.templateTable.keys():
                self.templateTable[tpl_offset] = {tpl_id: ra}

            if tpl_id not in self.templateTable[tpl_offset].keys():
                real_offset = self.chunk_start + tpl_offset
                if ra == real_offset:
                    self.templateTable[tpl_offset].update({tpl_id: ra})
                else:
                    raise InvalidBinXMLException("read_template()", self.buf.tell(), self.offset)
                    # print("tell: ", self.buf.tell(), "ra: ", ra)
                    # print("templateId", tpl_id, "templateOffset", tpl_offset)
                    # print(self.templateTable)
                    # exit(-1)

            try:
                if ra == self.templateTable[tpl_offset][tpl_id]:
                    templateDef = TemplateDefinition(self.buf, self.offset)
                    self.templateSize = templateDef.data_size
                    self.update()
                    self.start_sarray = self.buf.tell() + templateDef.data_size
                    # print("start_sarray", self.start_sarray)
                    self.read_sarray()
                else:
                    self.start_sarray = ra
                    # print("start_sarray", self.start_sarray)
                    self.read_sarray()
                    self.offset = self.templateTable[tpl_offset][tpl_id]
                    templateDef = TemplateDefinition(self.buf, self.offset)
                    self.templateSize = templateDef.data_size
                    self.update()

            except KeyError:
                print("[Not Found Template]", self.buf.tell(), self.offset, tpl_offset)
                exit(-1)

            fragTid2 = self.read_byte()
            if TOKEN_LOOKUP_TABLE[fragTid2] is 'FragmentHeader':
                FragmentHeader(self.buf, self.offset)
            else:
                raise InvalidBinXMLException("read_template()_else(1)", self.buf.tell(), self.offset)
        else:  # element가 바로 나오는 경우?
            raise InvalidBinXMLException("read_template()_else(2)", self.buf.tell(), self.offset)

    def read_sarray(self):
        ra = self.buf.tell()
        self.buf.seek(self.start_sarray)
        slookup = list()
        count = self.read_int()
        if count == 0:
            self.buf.seek(ra)
            return
            # raise NotImplementedError
        for i in range(count):
            slookup.append(list((struct.unpack(SUBSTITUTION_ARR_FORMAT, self.buf.read(4)))))

        for size, type, _ in slookup:
            # 이 부분을 수정해서 binxml 타입인 경우 새롭게 파싱해주도록 해야 함
            if type is 0x21:
                self.update()
                e = BinXML(self.buf, self.offset, size, self.templateTable, self.stringTable).root
            else:
                if (type & 0x80) == 0x80:  # Array Type
                    v = self.buf.read(size)
                    e = VALUE_TYPES[type ^ 0x80](v, size, True)
                else:
                    # print(self.buf.tell(), self.offset, size, type)
                    v = self.buf.read(size)
                    e = VALUE_TYPES[type](v, size, False)
            self.sArray.append(e)

        self.buf.seek(ra)

    def print_xml(self):
        indent(self.root)
        dump(self.root)


class Token(MmFile):
    """ Token Class """
    def __init__(self, buf, offset, tid, stringT, sArray):
        super(Token, self).__init__(buf, offset)
        self.tid = tid
        self.stringTable = stringT
        self.sArray = sArray
        self.name = unicode()
        self.attrib = list()
        self.value = list()
        self.content = None
        self.empty = None
        self.end = False
        self.EOF = False
        self.child = False
        self.parser()

    def __repr__(self):
        return "BinXML Token(Name = {})".format(self.name)

    def parser(self):
        # stage 0: token type check
        if TOKEN_LOOKUP_TABLE[self.tid] is 'OpenStart':

            # stage 1: get a element's name
            name_id = self.open_start()  # ofs + ELEMENT_START_SZ + 4
            ra = self.buf.tell()
            self.name = self.get_name(name_id, ra)

            # stage 2: get a element's attribute & value
            if self.has_attrib():
                for a, v in self.attribute(False):
                    self.attrib.append(a)
                    self.value.append(v)

            # stage 3: check a close and contents
            if self.has_content():
                check_token = self.preview()
                self.update()
                if TOKEN_LOOKUP_TABLE[check_token] is not 'OpenStart':
                    if check_token is 0x04:
                        self.content = None
                    else:
                        self.content = Content(self.buf, self.offset, self.sArray).read_text()
                    # stage 4: check a end(</>) token
                    end = self.read_byte()
                    if TOKEN_LOOKUP_TABLE[end] is 'End':
                        pass
                    else:
                        self.child = True

        elif TOKEN_LOOKUP_TABLE[self.tid] is 'End':
            self.end = True

        elif TOKEN_LOOKUP_TABLE[self.tid] is 'EOF':
            self.EOF = True

        elif TOKEN_LOOKUP_TABLE[self.tid] is 'OptionalSubstitution':
            # 이때 subroot에 대한 정확한 파싱과 element 추가가 필요
            self.name = u"SubRoot"
            self.content = Content(self.buf, self.offset - 1, self.sArray).read_text()

        # Not Found Start Token
        else:
            print("[Not Found Start Token Error]", self.tid, self.buf.tell(), self.offset)
            raise NotImplementedError

    def open_start(self):
        binToken = self.buf.read(ELEMENT_START_SZ)
        fields = dict(zip(ELEMENT_START_FIELDS, struct.unpack(ELEMENT_START_FORMAT, binToken)))
        for key in fields:
            setattr(self, key, fields[key])
        return getattr(self, 'name_offset')

    def attribute(self, r):
        # stage 0: Attribute list, Data size
        if not r:
            # attribSize = struct.unpack('I', self.buf.read(4)) # 이 값을 이용해서 검증해주는 루틴을 적용하는 것도 나쁘지 않음.
            struct.unpack('I', self.buf.read(4))
        # stage 1: parsing the data
        attrib_tid = self.read_byte()

        if TOKEN_LOOKUP_TABLE[attrib_tid] is 'Attribute':
            name_id = self.read_int()
            ra = self.buf.tell()
            attribName = self.get_name(name_id, ra)

            value = Content(self.buf, self.offset, self.sArray).read_text()

            if self.has_more_attribute(attrib_tid):
                yield attribName, value
                self.update()
                for a, v in self.attribute(True):
                    yield a, v
            else:
                yield attribName, value
        else:
            raise InvalidBinXMLException("attribute()",
                                         self.buf.tell(), self.offset)

    def has_attrib(self):
        return (self.tid is 0x41)

    def has_content(self):
        close_tid = ord(self.buf.read(1))
        if 'Close' in TOKEN_LOOKUP_TABLE[close_tid]:
            return (close_tid is 0x02)
        else:
            raise InvalidBinXMLException("has_content()", self.buf.tell(), self.offset)

    def has_more_attribute(self, attrib_tid):
        return (attrib_tid is 0x46)

    def get_name(self, name_id, ra):

        if name_id in self.stringTable.keys():
            name_offset = self.stringTable[name_id]
            if ra == name_offset:
                name = NameString(self.buf, name_offset).read_name()
                self.update()
            else:
                name = NameString(self.buf, name_offset).read_name()
                self.offset = ra
                self.correct()

        else:
            chunk_start = int()
            for k, v in self.stringTable.items():
                chunk_start = v - k
                break
            name_offset = chunk_start + name_id
            if ra == name_offset:
                name = NameString(self.buf, name_offset).read_name()
                self.update()
            else:
                name = NameString(self.buf, name_offset).read_name()
                self.offset = ra
                self.correct()

        return name


class Content(MmFile):
    """ Content Token Type Class """
    def __init__(self, buf, offset, sArray):
        super(Content, self).__init__(buf, offset)
        self.cid = self.read_byte()
        self.text = None
        self.sArray = sArray
        ContentDispatchTable = {
            0x05: ValueText,
            0x07: CDATASection,
            0x08: CharRef,
            0x09: EntityRef,
            0x0a: PITarget,
            0x0b: PIData
        }
        SubstitutionDispatchTable = {
            0x0d: NormalSubstitution,
            0x0e: OptionalSubstitution
        }
        if self.cid in ContentDispatchTable.keys():
            self.objContent = ContentDispatchTable[self.cid](self.buf, self.offset)

        elif self.cid in SubstitutionDispatchTable.keys():
            self.objContent = SubstitutionDispatchTable[self.cid](self.buf, self.offset, self.sArray)

    def read_text(self):
        self.text = self.objContent.data
        self.update()
        return self.text


class TemplateInstance(MmFile):

    def __init__(self, buf, offset):
        super(TemplateInstance, self).__init__(buf, offset)
        templateIst = self.buf.read(TEMPLATE_IST_SZ)
        fields = dict(zip(TEMPLATE_IST_FIELDS, struct.unpack(TEMPLATE_IST_FORMAT, templateIst)))
        for key in fields:
            setattr(self, key, fields[key])

    def template_id(self):
        return getattr(self, 'template_id')

    def def_data_offset(self):
        return getattr(self, 'template_def_data_offset')


class TemplateDefinition(MmFile):

    def __init__(self, buf, offset):
        super(TemplateDefinition, self).__init__(buf, offset)
        templateDef = self.buf.read(TEMPLATE_DEF_SZ)
        fields = dict(zip(TEMPLATE_DEF_FIELDS, struct.unpack(TEMPLATE_DEF_FORMAT, templateDef)))
        for key in fields:
            setattr(self, key, fields[key])

    def data_size(self):
        return getattr(self, 'data_size')


class FragmentHeader(MmFile):

    def __init__(self, buf, offset):
        super(FragmentHeader, self).__init__(buf, offset)
        fragmentHdr = self.buf.read(FRAGMENT_HDR_SZ)
        fields = dict(zip(FRAGMENT_HDR_FIELDS, struct.unpack(FRAGMENT_HDR_FORMAT, fragmentHdr)))
        for key in fields:
            setattr(self, key, fields[key])


class ValueText(MmFile):

    def __init__(self, buf, offset):
        super(ValueText, self).__init__(buf, offset)
        self.valueType = ord(self.buf.read(1))
        self.update()
        if self.valueType is 0x01:
            self.data = UnicodeTextString(self.buf, self.offset).uniStr
            self.update()
        else:
            print(self.buf.tell(), self.valueType, self.offset)
            raise NotImplementedError


class CharRef(MmFile):

    def __init__(self, buf, offset):
        super(CharRef, self).__init__(buf, offset)
        raise NotImplementedError


class CDATASection(MmFile):

    def __init__(self, buf, offset):
        super(CDATASection, self).__init__(buf, offset)
        self.text = UnicodeTextString(buf, offset)
        raise NotImplementedError


class EntityRef(MmFile):

    def __init__(self, buf, offset):
        super(EntityRef, self).__init__(buf, offset)
        self.nameOffset = struct.unpack('I', self.buf.read(4))
        self.text = NameString(buf, offset)
        raise NotImplementedError


class PITarget(MmFile):

    def __init__(self, buf, offset):
        super(PITarget, self).__init__(buf, offset)
        self.text = NameString(buf, offset)
        raise NotImplementedError


class PIData(MmFile):

    def __init__(self, buf, offset):
        super(PIData, self).__init__(buf, offset)
        self.text = UnicodeTextString(buf, offset)
        raise NotImplementedError


class NormalSubstitution(MmFile):

    def __init__(self, buf, offset, sArray):
        super(NormalSubstitution, self).__init__(buf, offset)
        self.substId = struct.unpack('<H', self.buf.read(2))[0]
        self.valueType = self.read_byte()
        try:
            self.data = sArray[self.substId]
        except IndexError:
            print("{0:=^30}".format("NormalSubstitution"))
            print("buf.tell: {0}, offset: {1}".format(self.buf.tell(), self.offset))
            print("substId: {0}, valueType: {1}".format(self.substId, self.valueType))
            print("sArray")
            print(sArray)
            print("=" * 30)
            exit(-1)


class OptionalSubstitution(MmFile):

    def __init__(self, buf, offset, sArray):
        super(OptionalSubstitution, self).__init__(buf, offset)
        self.substId = struct.unpack('<H', self.buf.read(2))[0]
        self.valueType = self.read_byte()
        try:
            self.data = sArray[self.substId]
        except IndexError:
            print("{0:=^30}".format("OptionalSubstitution"))
            print("buf.tell: {0}, offset: {1}".format(self.buf.tell(), self.offset))
            print("substId: {0}, valueType: {1}".format(self.substId, self.valueType))
            print("sArray")
            print(sArray)
            print("=" * 30)
            exit(-1)


class NameString(MmFile):

    def __init__(self, buf, offset):
        super(NameString, self).__init__(buf, offset)
        buf = self.buf.read(NAME_STRING_SZ)
        fields = dict(zip(NAME_FIELDS, struct.unpack(NAME_FORMAT, buf)))
        for key in fields:
            setattr(self, key, fields[key])

    def read_name(self):
        name = unicode()
        nameLength = getattr(self, 'length')
        for i in range(nameLength + 1):
            nameChar = self.buf.read(2)
            name += nameChar.decode('utf16')
        return name[:-1]


class UnicodeTextString(MmFile):

    def __init__(self, buf, offset):
        super(UnicodeTextString, self).__init__(buf, offset)
        self.uniStr = unicode()
        length = struct.unpack('<H', self.buf.read(2))[0]
        for i in range(length):
            uniChar = self.buf.read(2)
            self.uniStr += uniChar.decode('utf16')
