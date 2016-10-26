#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# send_cmd.py


# ---- IMPORTS

import os
import re
import time
import sys
import serial
import struct
from optparse import OptionParser, OptionGroup

sys.path.insert(0, 'subupy')
from core import SubUpySerial, SubUpyUtility

# ---- CONSTANTS

VERBOSE = 0

AUTHOR = u"zealotnt"

VERSION = "0.0.1"

PROG = "send_cmd"

COPYRIGHT = u"Copyright © 2016"

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

# ---- GLOBALS

# ---- MAIN

if __name__ == "__main__":

	return_code = 0

	parser = OptionParser()

	parser.add_option(  "-s", "--serial",
						dest="serial",
						type="string",
						help="define the serial port to use")
	parser.add_option(  "-v", "--verbose",
						action="count",
						dest="verbose",
						help="enable verbose mode")
	parser.add_option(  "-l", "--list-serial",
						action="store_true",
						dest="list_serial",
						default=False,
						help="display available serial ports")

	(options, args) = parser.parse_args()

	if options.list_serial:
		print "Available serial ports:"
		for port_name in scan():
			print '  - ' + port_name
		sys.exit(0)

	if options.serial is not None:
		serial = options.serial
	else:
		serial = DEFAULT_SERIAL_PORT
		print "No serial port specified, use " + DEFAULT_SERIAL_PORT + " as default"

	port_name = serial

	if options.verbose >= VERBOSE:
		print 'Open serial port: ' + port_name

	commander = SubUpySerial(port_name, 115200)

	# response = commander.SendCmd(r"print('1\n\n\n123\r\n123132')")
	# print "The board response: " + response
	# dump_hex(response, "The board response: ")

	# resp = SubUpyUtility.ListFile(commander)
	# print resp
	# print type(resp)

	string_to_write = r"Specify \'wb\' as the second argument to open() to open for writing in binary mode"
	resp = SubUpyUtility.WriteFile(commander, 'main.py', string_to_write)
	resp = SubUpyUtility.ReadFile(commander, 'main.py')
	print resp