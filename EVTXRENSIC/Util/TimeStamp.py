from datetime import datetime, timedelta

# v = 131210007740281591, binary data, little endian, long
def filetime(v):
    dt = "{0:x}".format(v)
    us = int(dt, 16) / 10.
    return datetime(1601, 1, 1) + timedelta(microseconds = us)
