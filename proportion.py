#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import projections
from OsmData import OsmData

def main():
	if len(sys.argv) != 3:
		return 0
	tData = OsmData()
	# tData.addcomment("Done.")
	tData.addcomment("Hello World.")
	tData.write(sys.stdout)

if __name__ == '__main__':
	main()
