import sublime
import sublime_plugin
import subprocess
import threading
import os, serial, sys, glob

settings = sublime.load_settings('subupy.sublime-settings')

#Select and save port settings
class SerialSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if settings.has("port"):
            print('get_setting: ,' + settings.get("port", None))
        else:
            settings.set("port", "test")
            sublime.save_settings('subupy.sublime-settings')

    def is_checked(self):
        return False

class SerialWriteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print(SerialPort.GetPorts())

class SerialReadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print(SerialPort.GetPorts())


class SerialPort():
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
    def Write(buf):
        pass

    @staticmethod
    def ListFile():
        pass

    @staticmethod
    def ReadFile(name):
        pass
