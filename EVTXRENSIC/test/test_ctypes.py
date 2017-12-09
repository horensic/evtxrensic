import os
import re
from ctypes import *
#from ctypes.wintypes import *
from _winreg import *

p = re.compile("(\%.*\%)")
mydll = cdll.LoadLibrary('LogMessage')

eventlogkey = "SYSTEM\CurrentControlSet\Services\EventLog"

with OpenKey(HKEY_LOCAL_MACHINE, eventlogkey + "\System\FltMgr") as key:
    EventMessageFile = QueryValueEx(key, "EventMessageFile")[0]
    libList = EventMessageFile.split(';')

    for lib in libList:
        envKey = (re.findall(p, lib)[0]).replace("%", "")
        lib = re.sub(p, os.environ[envKey], lib)
        lib = u"C:\\WINDOWS\\system32\\ko-KR\\services.exe.mui"
        paramList = [u"0", u"5", u"0", u"18", u"MeDvpDrv", u"2017"]
        #ssbuf = create_unicode_buffer(4096)
        paramArray = (c_wchar_p * len(paramList))()
        paramArray[:] = paramList
        fMsg = create_unicode_buffer(4096)
        ret = mydll.EventLogMessage(fMsg, lib, paramArray, 0x40001B85)
        print(fMsg.value)
