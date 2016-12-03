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
def HtmlMessage(text, color="gray"):
    return """
            <body id=show-scope>
                <style>
                    p {
                        margin-top: 0;
                        margin-bottom: 0;
                        color: %s
                    }
                    a {
                        font-family: sans-serif;
                        font-size: 1.05rem;
                    }
                </style>
                <p>%s</p>
            </body>
        """ % (color, text)

def PopUpMessage(view, text, color="gray"):
    scope = view.scope_name(view.sel()[-1].b)
    html = HtmlMessage(text, color)
    view.show_popup(html, on_navigate=lambda x: copy(view, x))

class SubUpyConnectPort(sublime_plugin.WindowCommand):
    def selected_callback(self, selected_index):
        if settings.has("port"):
            print('Closing %s' % settings.get("port", None))
            # TODO: Close the current opened com port
        port = avail_ports[selected_index]
        settings.set("port", port)
        sublime.save_settings('subupy.sublime-settings')
        global gserial
        gserial = SubUpySerial(port, 115200)

        # Promt message to user
        sublime.status_message("%s opened successfully !" % port)
        PopUpMessage(self.window.active_view(), "%s opened successfully !" % port)

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
        sublime.status_message("%s saved successfully !" % file_name)
        PopUpMessage(self.window.active_view(), "%s saved successfully !" % file_name)

class SubUpyDeleteFile(sublime_plugin.WindowCommand):
    def selected_callback(self, selected_index):
        if selected_index == -1:
            return
        deleted_file = files[selected_index]
        SubUpyUtility.RemoveFile(gserial, deleted_file)
        sublime.status_message("File %s deleted" % deleted_file)
        print(self)
        PopUpMessage(self.window.active_view(), "File %s deleted" % deleted_file)

    def run(self):
        print(self)
        global files
        files = SubUpyUtility.ListFile(gserial)
        if len(files) == 0:
            # Pop up a error message box to show error
            sublime.status_message("No more file to delete")
            PopUpMessage(self.window.active_view(), "No more file to delete", "red")
            return
        sublime.active_window().show_quick_panel(files, self.selected_callback, flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)

class SubUpyOpenFile(sublime_plugin.WindowCommand):
    def selected_callback(self, selected_index):
        if selected_index == -1:
            return
        print(SubUpyUtility.ReadFile(gserial, files[selected_index]))

    def run(self):
        global files
        files = SubUpyUtility.ListFile(gserial)
        if len(files) == 0:
            sublime.status_message('No more file to open')
            PopUpMessage(self.window.active_view(), 'No more file to open', "red")
            return
        sublime.active_window().show_quick_panel(files, self.selected_callback, flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)
