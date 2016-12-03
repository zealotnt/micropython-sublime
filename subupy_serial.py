#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

#---- IMPORTS
import struct
import binascii
import time
import re
import ast
import os, sys, glob

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "serial"))
import serial

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

    def SendCmd(self, cmd, get_output=True, ctrtc_signal=False):
        # Send ctrl+c to abort current command line
        if ctrtc_signal == True:
            self._port.write(self.CODE_CTRL_C.encode('cp437'))
            self._port.flushOutput()
            # Wait until target able to receive new command
            if get_output == True:
                self.receiveRsp()

        # Append new line at the end of command
        self._port.write((cmd + "\n").encode('cp437'))
        self._port.flushOutput()

        # Receive the whole buffer from target
        if get_output == True:
            rcv_buff = self.receiveRsp()

        # Parse the output
        if get_output == False:
            return ""
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
                response += read_bytes.decode('cp437')

            if read_bytes == b'' and (time_check - time_start) > self.RECEIVE_TIMEOUT:
                return response

    def parseOutput(self, rcv_buff, cmd):
        response = ""

        # Find the line that contains the command
        match = re.findall(r'((.*\n)+)>>>', rcv_buff)

        if len(match) == 0:
            return response

        # If the command is not echoed, something error
        if match[0][0].find(cmd, 0) == -1:
            return ""

        # Remove the command from receive buffer
        response = match[0][0].replace(cmd, '')

        return response

class SubUpyUtility():
    @staticmethod
    def GetPorts():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    @staticmethod
    def ListFile(subupy_serial):
        subupy_serial.SendCmd("import os", ctrtc_signal=True)

        list_str = subupy_serial.SendCmd("os.listdir('./')")
        list_str = list_str.replace('\r\n', '')
        return ast.literal_eval(list_str)

    @staticmethod
    def ReadFile(subupy_serial, file_name):
        list_files = SubUpyUtility.ListFile(subupy_serial)
        if not (file_name in list_files):
            return None

        subupy_serial.SendCmd("f=open('" + file_name + "', 'r')", ctrtc_signal=True)
        response_str = subupy_serial.SendCmd("f.read()")
        subupy_serial.SendCmd("f.close()")
        if len(response_str) < 2:
            return ""

        # Remove the '' from the f.read()
        # match = re.findall(r"'((.*\n*)+)'", response_str)
        # if len(match) == 0:
        #     return ""
        # return match[0][0]

        return response_str

    @staticmethod
    def WriteFile(subupy_serial, file_name, file_data):
        subupy_serial.SendCmd("f=open('" + file_name + "', 'w')", ctrtc_signal=True)
        response_str = subupy_serial.SendCmd("f.write('" + file_data + "')")
        subupy_serial.SendCmd("f.close()")
        return response_str

    @staticmethod
    def RemoveFile(subupy_serial, file_name):
        list_files = SubUpyUtility.ListFile(subupy_serial)
        if not (file_name in list_files):
            return False

        subupy_serial.SendCmd("os.remove('" + file_name + "')")
        return True
