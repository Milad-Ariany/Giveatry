#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 16:53:10 2017

@author: milad
"""


def cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        print ( "Error in casting {} to {}".format(val, to_type) )
        return default

