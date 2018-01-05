#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 16:53:10 2017

@author: milad
"""

import datetime
def cast(val, to_type, default=None, _format=None):
    try:
        if type( to_type ) == datetime:
            if _format == None:
                return datetime.strptime(val, "%Y-%m-%d")
            return datetime.strptime(val, _format)
        return to_type(val)
    except (ValueError, TypeError):
        print ( "Error in casting {} to {}".format(val, to_type) )
        return default

