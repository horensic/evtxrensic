class WrongSignatureException(Exception):

    def __init__(self, msg):
        super(WrongSignatureException, self).__init__(msg)


class InvalidRecordException(Exception):

    def __init__(self):
        super(InvalidRecordException, self).__init__("Invalid Record Exception")


class InvalidChunkException(Exception):

    def __init__(self):
        super(InvalidChunkException, self).__init__("Invalid Chunk Exception")


class InvalidBinXMLException(Exception):

    def __init__(self, func, tell, offset):
        super(InvalidBinXMLException, self).__init__("Invalid BinXML Exception")
        print("{0} buf.tell(): {1}, offset: {2}".format(func, tell, offset))
