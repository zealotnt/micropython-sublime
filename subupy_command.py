#---- IMPORTS
import sublime
import sublime_plugin
import subprocess
import threading
import sys
import os
from subupy_serial import *

settings = sublime.load_settings('subupy.sublime-settings')

#Select and save port settings
class SubUpyConnectPort(sublime_plugin.ApplicationCommand):
    def selected_callback(self, selected_index):
        if settings.has("port"):
            print('Closing %s' % settings.get("port", None))
            # TODO: Close the current opened com port
        settings.set("port", avail_ports[selected_index])
        sublime.save_settings('subupy.sublime-settings')
        global gserial
        gserial = SubUpySerial(avail_ports[selected_index], 115200)

    def run(self):
        global avail_ports
        avail_ports = SubUpyUtility.GetPorts()
        print(SubUpyUtility.GetPorts())
        sublime.active_window().show_quick_panel(avail_ports, self.selected_callback, flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)

class SubUpySaveCurrentFile(sublime_plugin.WindowCommand):
    def run(self):
        body = self.window.active_view().substr(sublime.Region(0, self.window.active_view().size()))
        file_name = os.path.basename(self.window.active_view().file_name())
        SubUpyUtility.WriteFile(gserial, file_name, body)
        print("Save done")
        # TODO: pop up save success message

class SubUpyDeleteFile(sublime_plugin.ApplicationCommand):
    def selected_callback(self, selected_index):
        if selected_index == -1:
            return
        SubUpyUtility.RemoveFile(gserial, files[selected_index])
        print("File %s deleted" % files[selected_index])
        # TODO: print a delete success message

    def run(self):
        global files
        files = SubUpyUtility.ListFile(gserial)
        if len(files) == 0:
            # TODO: Pop up a error message box to show error
            print("No more file to delete")
            return
        sublime.active_window().show_quick_panel(files, self.selected_callback, flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)

class SubUpyOpenFile(sublime_plugin.ApplicationCommand):
    def selected_callback(self, selected_index):
        if selected_index == -1:
            return
        print(SubUpyUtility.ReadFile(gserial, files[selected_index]))

    def run(self):
        global files
        files = SubUpyUtility.ListFile(gserial)
        if len(files) == 0:
            # TODO: Pop up a error message box to show error
            print("No more file to open")
            return
        sublime.active_window().show_quick_panel(files, self.selected_callback, flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)
