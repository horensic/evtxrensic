# -*- coding: utf-8 -*-

import struct

# Fragment header
FRAGMENT_HDR_FORMAT = '<BBB'
FRAGMENT_HDR_FIELDS = ['major_version',
                       'minor_version',
                       'flags']

FRAGMENT_HDR_SZ = struct.calcsize(FRAGMENT_HDR_FORMAT)

# Name
NAME_FORMAT = '<IHH'
NAME_FIELDS = ['unknown',
               'hash',
               'length']

NAME_STRING_SZ = struct.calcsize(NAME_FORMAT)

# Element start
ELEMENT_START_FORMAT = '<HII'
ELEMENT_START_FIELDS = ['identifier',
                        'data_size',
                        'name_offset']

ELEMENT_START_SZ = struct.calcsize(ELEMENT_START_FORMAT)  # 6

# Template Instance
TEMPLATE_IST_FORMAT = '<BII'
TEMPLATE_IST_FIELDS = ['unknown1',
                       'template_id',
                       'template_def_data_offset']

TEMPLATE_IST_SZ = struct.calcsize(TEMPLATE_IST_FORMAT)

# Template definition
TEMPLATE_DEF_FORMAT = '<I16sI'
TEMPLATE_DEF_FIELDS = ['unknown',
                       'guid',
                       'data_size']

TEMPLATE_DEF_SZ = struct.calcsize(TEMPLATE_DEF_FORMAT)

# Substitution Array
SUBSTITUTION_ARR_FORMAT = '<HBB'





