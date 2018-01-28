#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 11:16:53 2018

@author: milad
"""

import Financial
import cProfile
import re
import pstats

Financial._interval_ = Financial.Interval.allYears
Financial._customeInterval_ = "2013"

find = Financial.MultiFinancialInfo( "fi-213.1.ADS.ETR" )   
#find.crawl()
# print (find.__dict__)

#print (find.results)
#for f in find.results:
#    print ( f.__dict__ )


# performance check
cProfile.run('find.crawl()', 'restats')
p = pstats.Stats('restats')
p.strip_dirs().sort_stats(-1).print_stats()