# -*- coding: utf-8 -*-

import struct

# EVTX Signature
EVTX_HDR_SIGNATURE = b'ElfFile\0'

# EVTX File Header
EVTX_HDR_FORMAT = '<8sQQQIHHHH76xII'
EVTX_HDR_FIELDS = ['signature',
                   'first_chunk_number',
                   'last_chunk_number',
                   'next_record_identifier',
                   'header_size',
                   'minor_version',
                   'major_version',
                   'header_block_size',
                   'number_of_chunks',
                   'unknown',
                   'file_flags',
                   'checksum']

EVTX_HDR_SZ = struct.calcsize(EVTX_HDR_FORMAT)  # 128

# Chunk Signature
EVTX_CHNK_HDR_SIGNATURE = b'ElfChnk\0'

# Chunk Header
EVTX_CHNK_HDR_FORMAT = '<8sQQQQIIII64x4xI'
EVTX_CHNK_HDR_FIELDS = ['signature',
                        'first_record_number',
                        'last_record_number',
                        'first_record_id',
                        'last_record_id',
                        'header_size',
                        'last_record_data_offset',
                        'free_space_offset',
                        'event_records_checksum',
                        'unknown1',
                        'unknown2',
                        'checksum']

EVTX_CHNK_HDR_SZ = struct.calcsize(EVTX_CHNK_HDR_FORMAT)  # 512

EVTX_CHNK_STRT_SZ = 256
EVTX_CHNK_TPL_SZ = 128

# Event record Signature
RECORD_HDR_SIGNATURE = b'\x2a\x2a\x00\x00'

# Event record Header
RECORD_HDR_FORMAT = '<4sIQQ'
RECORD_HDR_FIELDS = ['signature',
                     'size',
                     'event_record_id',
                     'timestamp']

RECORD_HDR_SZ = struct.calcsize(RECORD_HDR_FORMAT)  # 24

# Level

EVENT_LEVELS = {
    0x00000000: "LogAlways",
    0x00000001: "Critical",
    0x00000002: "Error",
    0x00000003: "Warning",
    0x00000004: "Informational",
    0x00000005: "Verbose",
    0x00000006: "ReservedLevel6",
    0x00000007: "ReservedLevel7",
    0x00000008: "ReservedLevel8",
    0x00000009: "ReservedLevel9",
    0x0000000A: "ReservedLevel10",
    0x0000000B: "ReservedLevel11",
    0x0000000C: "ReservedLevel12",
    0x0000000D: "ReservedLevel13",
    0x0000000E: "ReservedLevel14",
    0x0000000F: "ReservedLevel15"
}

# Keywords

EVENT_KEYWORDS = {
    0x0000000000000000: "AnyKeyword",
    0x0000000000010000: "Shell",
    0x0000000000020000: "Properties",
    0x0000000000040000: "FileClassStoreAndIconCache",
    0x0000000000080000: "Controls",
    0x0000000000100000: "APICalls",
    0x0000000000200000: "InternetExplorer",
    0x0000000000400000: "ShutdownUX",
    0x0000000000800000: "CopyEngine",
    0x0000000001000000: "Tasks",
    0x0000000002000000: "WDI",
    0x0000000004000000: "StartupPref",
    0x0000000008000000: "StructuredQuery",
    0x0001000000000000: "Reserved",
    0x0002000000000000: "WDIContext",
    0x0004000000000000: "WDIDiag",
    0x0008000000000000: "SQM",
    0x0010000000000000: "AuditFailure",
    0x0020000000000000: "AuditSuccess",
    0x0040000000000000: "CorrelationHint",
    0x0080000000000000: "Classic",
    0x0100000000000000: "ReservedKeyword56",
    0x0200000000000000: "ReservedKeyword57",
    0x0400000000000000: "ReservedKeyword58",
    0x0800000000000000: "ReservedKeyword59",
    0x1000000000000000: "ReservedKeyword60",
    0x2000000000000000: "ReservedKeyword61",
    0x4000000000000000: "ReservedKeyword62",
    0x8000000000000000: "ReservedKeyword63"
}