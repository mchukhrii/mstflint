# Copyright (C) Jan 2020 Mellanox Technologies Ltd. All rights reserved.   
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
# DumpData.py
# Python implementation of the Class DumpData
# Generated by Enterprise Architect
# Created on:      14-Aug-2019 10:12:02 AM
# Original author: talve
# 
#######################################################
from fetchers.ResourceDumpFetcher import ResourceDumpFetcher
from resource_data.QueryData import QueryData
from validation.ArgToMenuVerifier import ArgToMenuVerifier
from utils import constants as cs


class DumpData:
    """this class is responsible for getting the dump segment.
    """

    @classmethod
    def get_dump(cls, **kwargs):
        """this method is getting the menu segment by using QueryData and verify it with
        the user inputs using the ArgToMenuVerifier, if the verification pass, its uses
        the core dump fetcher to fetch the core dump segments.
        """
        dump_segments = None

        # get the query data
        # need to call query data
        res = QueryData.get_query(kwargs["device_name"], kwargs["vHCAid"])

        # validate that the dump supported by calling ArgToMenuVerifier
        rc = ArgToMenuVerifier.verify(res, **kwargs)

        # if args passes the verify
        if rc:
            # segment type can be name, this method will convert the name (if needed) to seg number in hex (str)
            kwargs[cs.UI_ARG_SEGMENT] = res.get_segment_type_by_segment_name(kwargs[cs.UI_ARG_SEGMENT])
            dump_segments = ResourceDumpFetcher(kwargs["device_name"]).fetch_data(**kwargs)
        else:
            raise Exception("not supported or missing argument")

        return dump_segments

