# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

import argparse
import Options, Bonds, Stocks


parser = argparse.ArgumentParser(description='Run custom scraping programs')
parser.add_argument('-t', required=True, help='which scraper to run??, default=optionstest')
args = parser.parse_args()

if args.t == 'options':
    Options.get_options()
elif args.t == 'optionstest':
    Options.test()
else:
    print("INVALID CHOICE!!")
    

