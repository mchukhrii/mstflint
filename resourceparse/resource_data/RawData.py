# Copyright (C) Jan 2020 Mellanox Technologies Ltd. All rights reserved.
# Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# This software is available to you under a choice of one of two
# licenses.  You may choose to be licensed under the terms of the GNU
# General Public License (GPL) Version 2, available from the file
# COPYING in the main directory of this source tree, or the
# OpenIB.org BSD license below:
#
#     Redistribution and use in source and binary forms, with or
#     without modification, are permitted provided that the following
#     conditions are met:
#
#      - Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      - Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials
#        provided with the distribution.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --


#######################################################
#
# RawData.py
# Python implementation of the Class RawData
# Generated by Enterprise Architect
# Created on:      19-Dec-2019 3:18:40 PM
# Original author: talve
#
#######################################################
import binascii
from utils import constants as cs
from segments.SegmentCreator import SegmentCreator
import json
import re


class RawData:
    """This class is responsible for getting the dumped data according the supported
    inputs (devlink - json, resourcedump - bin file or resourcedump - human
    readable) and generate a unified raw data divided to the specific segments and
    ready for parse.
    """
    def __init__(self, dumped_file_path):
        """initialize class members.
        """
        self._file_path = dumped_file_path
        self._segments_raw_data = []

    def _determine_dump_type(self):
        """This method responsible for analyzing the the dumped file and return the file
        type.
        """
        file_type = cs.RAW_DATA_FILE_TYPE_BIN
        if not self.is_binary():
            if self.is_json():
                file_type = cs.RAW_DATA_FILE_TYPE_JSON
            else:
                file_type = cs.RAW_DATA_FILE_TYPE_HUMAN_READABLE
        return file_type

    def is_json(self):
        """This method check if the file type is json format.
        """
        try:
            with open(self._file_path) as check_file:  # try open file and open it as json
                json.load(check_file)
                return True
        except Exception as _:  # if fail then file is not json
            return False

    def is_binary(self):
        """This method check if the file type is binary format.
        """
        with open(self._file_path, 'rb') as f:
            if b'\x00' in f.read():
                return True
            else:
                return False

    def _gathered_raw_data_according_dump_type(self):
        """This method responsible for generate the segment data according the file type.
        """
        # get the file type
        file_type = self._determine_dump_type()

        # retrieve the raw data from the file
        if file_type == cs.RAW_DATA_FILE_TYPE_BIN:
            return self._retrieve_raw_data_from_bin_file()
        elif file_type == cs.RAW_DATA_FILE_TYPE_JSON:
            return self._retrieve_raw_data_from_json_file()
        elif file_type == cs.RAW_DATA_FILE_TYPE_HUMAN_READABLE:
            return self._retrieve_raw_data_human_readable_file()

    def to_segments(self):
        """This method return a list of segments objects according the dumped file input.
        """
        raw_data = self._gathered_raw_data_according_dump_type()
        return SegmentCreator().create(raw_data)

    @classmethod
    def _build_dw_from_bytes(cls, byte_0, byte_1, byte_2, byte_3):
        """This method convert 4 bytes to a double word.
        """
        return (byte_0 << 24) + (byte_1 << 16) + (byte_2 << 8) + byte_3

    def _retrieve_raw_data_from_bin_file(self):
        """This method go over the bin file and collect the raw data.
        """
        segments_raw_data = []
        with open(self._file_path, "rb") as f:
            bytes_read = f.read(cs.RAW_DATA_CHUNK_SIZE_IN_BYTES)
            while bytes_read:
                segments_raw_data.append(int(binascii.hexlify(bytes_read[:]), 16))
                bytes_read = f.read(cs.RAW_DATA_CHUNK_SIZE_IN_BYTES)
        return segments_raw_data

    def _retrieve_raw_data_from_json_file(self):
        """This method go over the json file and collect the raw data.
        """
        with open(self._file_path) as f:  # try open file and open it as json
            data_dict = json.load(f)
            self._collect_all_data_sections(data_dict)
            return self._segments_raw_data

    def _collect_all_data_sections(self, json_node):
        """This method read all the data fields recursively.
        """
        if isinstance(json_node, dict):
            for key, value in json_node.items():
                if key != "data":
                    self._collect_all_data_sections(value)
                else:
                    for i in range(0, len(value), 4):
                        dw = self._build_dw_from_bytes(value[i], value[i + 1], value[i + 2], value[i + 3])
                        self._segments_raw_data.append(dw)
        elif isinstance(json_node, list):
            for node in json_node:
                self._collect_all_data_sections(node)

    def _retrieve_raw_data_human_readable_file(self):
        """This method go over the human readable text file and collect the raw data.
        """
        with open(self._file_path, 'r') as f:
            for line in f:
                if line.find("Segment Type") == cs.PARSER_STRING_NOT_FOUND:
                    if re.search(r"0x[0-9a-fA-F]{8}", line):
                        hex_list = re.findall(r"0x[0-9a-fA-F]{8}", line)
                        for hex_number in hex_list:
                            self._segments_raw_data.append(int(hex_number, 16))
        return self._segments_raw_data
