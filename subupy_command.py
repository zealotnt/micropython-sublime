#---- IMPORTS
import sublime
import sublime_plugin
import subprocess
import threading

settings = sublime.load_settings('subupy.sublime-settings')

#Select and save port settings
class SubUpyConnectPort(sublime_plugin.ApplicationCommand):
    def selected_callback(self, selected_index):
        if settings.has("port"):
            print('connect san roi close %s cai da' % settings.get("port", None))
            # TODO: Close the current opened com port
        settings.set("port", avail_ports[selected_index])
        sublime.save_settings('subupy.sublime-settings')

    def run(self):
        global avail_ports
        avail_ports = SubUpyUtility.GetPorts()
        print(SubUpyUtility.GetPorts())
        sublime.active_window().show_quick_panel(avail_ports, self.selected_callback, flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)

class SubUpySaveCurrentFile(sublime_plugin.ApplicationCommand):
    def run(self):
        print("Write current file ne")

class SubUpyDeleteFile(sublime_plugin.ApplicationCommand):
    def run(self):
        print("Delete file ne")

class SubUpyOpenFile(sublime_plugin.ApplicationCommand):
    def run(self):
        print("Open file ne")
