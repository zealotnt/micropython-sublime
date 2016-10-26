#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

#---- IMPORTS
import serial
import struct
import binascii
import time
import re
import ast

#---- CONSTANT

#---- CLASSES
class SubUpySerial():
	"""
	SubUpySerial extends `Serial` by adding functions to read/write subupy commands.
	"""
	# worst-case byte-to-byte time is 100ms
	CHAR_TIMEOUT = 0.1
	RECEIVE_TIMEOUT = 10
	CODE_CTRL_C = '\x03'

	def __init__(self, port, baud):
		"""
		:Parameter port: serial port to use (/dev/tty* or COM*)
		"""
		self._port = serial.Serial(port=port, baudrate=baud, timeout=self.CHAR_TIMEOUT)

	def SendCmd(self, cmd):
		# Append new line at the end of command
		cmd += "\r\n"

		# Send ctrl+c to abort current command line
		self._port.write(self.CODE_CTRL_C)

		# Write the command
		self._port.flushInput()
		self._port.write(cmd)

		# Receive the whole buffer from target
		rcv_buff = self.receiveRsp()

		# Parse the output
		return self.parseOutput(rcv_buff, cmd)

	def receiveRsp(self):
		# Receive until timeout
		response = ""
		time_start = float(time.time() * 1000)
		while True:
			time_check = float(time.time() * 1000)
			waiting = self._port.inWaiting()
			read_bytes = self._port.read(1 if waiting == 0 else waiting)

			if len(read_bytes) != 0:
				time_start = float(time.time() * 1000)
				response += read_bytes

			if read_bytes == '' and (time_check - time_start) > self.RECEIVE_TIMEOUT:
				return response

	def parseOutput(self, rcv_buff, cmd):
		response = ""

		# Find the line that contains the command
		match = re.findall(r'>>> ((.*\n)+)>>>', rcv_buff)

		if len(match) == 0:
			return response

		# If the command is not echoed, something error
		if match[0][0].find(cmd, 0) != 0:
			return ""

		# Remove the command from receive buffer
		response = match[0][0].replace(cmd, '')

		return response

class SubUpyUtility():
	@staticmethod
	def ListFile(subupy_serial):
		subupy_serial.SendCmd("import os")

		list_str = subupy_serial.SendCmd("os.listdir()")
		list_str = list_str.replace('\r\n', '')
		return ast.literal_eval(list_str)

	@staticmethod
	def ReadFile(subupy_serial, file_name):
		list_files = SubUpyUtility.ListFile(subupy_serial)
		if not (file_name in list_files):
			return None

		subupy_serial.SendCmd("f=open('" + file_name + "', 'r')")
		response_str = subupy_serial.SendCmd("f.read()")
		subupy_serial.SendCmd("f.close()")
		if len(response_str) < 2:
			return ""

		# Remove the '' from the f.read()
		# match = re.findall(r"'((.*\n*)+)'", response_str)
		# if len(match) == 0:
		# 	return ""
		# return match[0][0]

		return response_str

	@staticmethod
	def WriteFile(subupy_serial, file_name, file_data):
		subupy_serial.SendCmd("f=open('" + file_name + "', 'w')")
		response_str = subupy_serial.SendCmd("f.write('" + file_data + "')")
		subupy_serial.SendCmd("f.close()")
		return response_str

	@staticmethod
	def RemoveFile(subupy_serial, file_name):
		list_files = SubUpyUtility.ListFile(subupy_serial)
		if not (file_name in list_files):
			return False

		subupy_serial.SendCmd("import os")
		subupy_serial.SendCmd("os.remove('" + file_name + "')")
		return True
