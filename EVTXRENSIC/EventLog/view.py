# -*- coding: utf-8 -*-

import os
import re
from .defines import *
from ctypes import *
from _winreg import *
from xml.etree.ElementTree import Element, dump

from BinXML.binxml import indent

class RecordView(object):

    def __init__(self, root):
        self.binXmlRoot = root
        self.eventSourceName = None
        self.qualifiers = None
        self.time = unicode()
        self.get_element()
        self.get_keywords()
        self.get_level()

    def get_element(self):
        for parent in self.binXmlRoot:
            if parent.tag == u"System":
                # provider - event source name
                provider = parent.find(u"Provider")
                if u"EventSourceName" in provider.attrib:
                    self.eventSourceName = parent.find(u"Provider").attrib[u"EventSourceName"]
                    self.name = parent.find(u"Provider").attrib[u"Name"]
                else:
                    self.name = parent.find(u"Provider").attrib[u"Name"]
                # event id
                self.eventId = parent.find(u"EventID").text
                if u"Qualifiers" in parent.find(u"EventID").attrib:
                    self.qualifiers = parent.find(u"EventID").attrib[u"Qualifiers"]
                # channel
                self.channel = parent.find(u"Channel").text
                # task
                self.task = parent.findtext(u"Task")
                # TimeCreate
                timeCreated = parent.find(u"TimeCreated")
                if u"SystemTime" in timeCreated.attrib:
                    self.time = timeCreated.attrib[u"SystemTime"]
                # EventRecordId
                self.recordId = parent.findtext(u"EventRecordID")


            elif parent.tag == u"EventData":
                self.paramList = [data.text for data in parent.findall(u"Data")]

            elif parent.tag == u"UserData":
                if parent.findall(u"Data") is not None:
                    self.paramList = [data.text for data in parent.findall(u"Data")]
                else:
                    self.paramList = []

            else:
                # TODO exception 처리 해주기
                print("error?")
                indent(self.binXmlRoot)
                dump(self.binXmlRoot)
                exit(-1)


    def get_message(self):
        logMsg = cdll.LoadLibrary('.\EventLog\LogMessage')
        eventLogKey = "SYSTEM\CurrentControlSet\Services\EventLog"

        if self.eventSourceName is not None:
            regKeyPath = eventLogKey + "\\" + self.channel + "\\" + self.eventSourceName  # join 테스트 후 바꿔주기
        else:
            regKeyPath = eventLogKey + "\\" + self.channel + "\\" + self.name  # join 테스트 후 바꿔주기
        # print(regKeyPath)
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, regKeyPath)
        except WindowsError as ErrorOpenKey:    # 혹시나 키가 존재하지 않을 경우, 이 경우는 이벤트 로그를 발생시킨 source가 분석 시스템에 없음.
            print("Failed OpenKey with LastError", ErrorOpenKey)
            # TODO return -1? or exit(-1)?
        else:
            with key:
                try:
                    eventMsgFile = QueryValueEx(key, "EventMessageFile")[0]
                    msgFileList = eventMsgFile.split(';')

                except WindowsError as ErrorQueryValue:
                    print("Failed QueryValueEx with LastError", ErrorQueryValue)
                    # TODO return -1? or ...

                else:
                    for msgFile in msgFileList:
                        msgFile = os.path.expandvars(msgFile)
                        # print("msgFile: ", msgFile)

                        if self.qualifiers is not None:
                            eventId = hex(int(self.qualifiers) << 16 | int(self.eventId))
                        else:
                            eventId = hex(int(self.eventId))

                        paramArray = (c_wchar_p * len(self.paramList))()  # it's ok

                        paramArray[:] = self.paramList
                        fMsg = create_unicode_buffer(4096)
                        try:
                            ret = logMsg.EventLogMessage(fMsg, msgFile, paramArray, int(eventId, 0))
                        except WindowsError as err:
                            print(err)
                        else:
                            if (ret == 317):
                                originPath = os.path.split(msgFile)
                                retryPath = os.path.join(originPath[0], u"ko-KR", originPath[1] + u".mui")
                                # print("retryPath: ", retryPath)
                                try:
                                    ret = logMsg.EventLogMessage(fMsg, retryPath, paramArray, int(eventId, 0))
                                except WindowsError as err:
                                    print(err)
                                else:
                                    print(fMsg.value)
                            else:
                                print(fMsg.value)

    def get_keywords(self):
        # delete reserved keyword
        for parent in self.binXmlRoot:
            if parent.tag == u"System":
                keyword = parent.findtext("Keywords")
                if keyword is not None:
                    key = long(keyword, 0) & 0x00ffffffffffffff
                    try:
                        self.keywords = EVENT_KEYWORDS[key]
                        # print(self.keywords)
                    except KeyError as e:
                        # print(e)
                        self.keywords = "N/A"
                else:
                    print("keyword", keyword)
                    exit(-1)

    def get_level(self):
        for parent in self.binXmlRoot:
            if parent.tag == u"System":
                key = parent.findtext("Level")
                if key is not None:
                    self.level = EVENT_LEVELS[int(key)]
                    # print(self.level)
                else:
                    print("level", key)
                    exit(-1)
