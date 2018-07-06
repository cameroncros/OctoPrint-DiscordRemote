import collections
import humanfriendly
import re
import time
import requests

from octoprint.printer import InvalidFileLocation, InvalidFileType
from terminaltables import AsciiTable as Table

from command_plugins import plugin_list


class Command:
    def __init__(self, plugin):
        assert plugin
        self.plugin = plugin
        self.command_dict = collections.OrderedDict()
        self.command_dict['/connect'] = {'cmd': self.connect, 'params': "[port] [baudrate]", 'description': "Connect to a printer."}
        self.command_dict['/disconnect'] = {'cmd': self.disconnect, 'description': "Disconnect from a printer."}
        self.command_dict['/print'] = {'cmd': self.start_print, 'params': "{filename}", 'description': "Print a file."}
        self.command_dict['/files'] = {'cmd': self.list_files, 'description': "List all the files."}
        self.command_dict['/abort'] = {'cmd': self.cancel_print, 'description': "Abort a print."}
        self.command_dict['/snapshot'] = {'cmd': self.snapshot, 'description': "Take a snapshot with the camera."}
        self.command_dict['/status'] = {'cmd': self.status, 'description': "Get the current printer status."}
        self.command_dict['/help'] = {'cmd': self.help, 'description': "Print this help."}
        self.command_dict['/pause'] = {'cmd': self.pause, 'description': "Pause current print."}
        self.command_dict['/resume'] = {'cmd': self.resume, 'description': "Resume current print."}

        # Load plugins
        for command_plugin in plugin_list:
            command_plugin.setup(self, plugin)

    def parse_command(self, string):
        parts = re.split('\s+', string)

        command = self.command_dict.get(parts[0])
        if command is None:
            if parts[0][0] == "/" or \
                    parts[0].lower() == "help":
                return self.help()
            return None, None

        if command.get('params'):
            return command['cmd'](parts)
        else:
            return command['cmd']()

    def help(self):
        data = [["Command",
                 "Parameters and Description"]]

        for command, details in self.command_dict.items():
            data.append([command, details.get('params') or ""])
            data.append(["", details.get('description')])
            data.append([])

        table = Table(data)
        message = str(table.table)
        return message, None

    def cancel_print(self):
        self.plugin._printer.cancel_print()
        return "Print aborted", None

    def start_print(self, params):
        if len(params) != 2:
            return "Wrong number of arguments, try 'print [filename]'", None
        if not self.plugin._printer.is_ready():
            return "Printer is not ready", None

        file = self.find_file(params[1])
        if file is None:
            return "Failed to find the file", None

        is_sdcard = (file['location'] == 'sdcard')
        try:
            file_path = self.plugin._file_manager.path_on_disk(file['location'], file['path'])
            self.plugin._printer.select_file(file_path, is_sdcard, printAfterSelect=True)
        except InvalidFileType:
            return "Invalid file type selected", None
        except InvalidFileLocation:
            return "Invalid file location?", None

        return "Successfully started print: %s" % file['path'], None

    def list_files(self):
        file_list = self.get_flat_file_list()
        data = [["File", "Details"]]
        for details in file_list:
            try:
                data.append([details['path']])
            except:
                pass

            try:
                data.append(["Location", details['location']])
            except:
                pass

            try:
                estimated_print_time = humanfriendly.format_timespan(details['analysis']['estimatedPrintTime'],
                                                                     max_units=2)
                data.append(["Estimated Print Time", estimated_print_time])
            except:
                pass

            try:
                average_print_time = humanfriendly.format_timespan(
                    details['statistics']['averagePrintTime']['_default'], max_units=2)
                data.append(["Average Print Time", average_print_time])
            except:
                pass

            try:
                filament_required = humanfriendly.format_length(
                    details['analysis']['filament']['tool0']['length'] / 1000)
                data.append(["Filament Required", filament_required])
            except:
                pass

            data.append([])  # Add a spacer.

        table = Table(data)
        return str(table.table), None

    def snapshot(self):
        return None, self.plugin.get_snapshot()

    def find_file(self, file_name):
        flat_filelist = self.get_flat_file_list()
        for file in flat_filelist:
            if file_name in file.get('path'):
                return file
        return None

    def get_flat_file_list(self):
        file_list = self.plugin._file_manager.list_files(recursive=True)
        flat_filelist = []
        for (location, files) in file_list.items():
            self.flatten_file_list_recursive(flat_filelist, location, files, "")

        return flat_filelist

    def flatten_file_list_recursive(self, file_array, location, files, path):
        for filename, details in files.items():
            if details.get('children') is not None:
                # This is a folder, recurse into it
                self.flatten_file_list_recursive(file_array, location, details['children'], filename)
            else:
                if path == "" or not path.endswith("/"):
                    path += "/"
                details['path'] = path + filename
                details['location'] = location
                file_array.append(details)

    def connect(self, params):
        if len(params) > 3:
            return "Too many parameters. Should be: /connect [port] [baudrate]", None
        if self.plugin._printer.is_operational():
            return 'Printer already connected. Disconnect first', None

        port = None
        baudrate = None
        if len(params) >= 2:
            port = params[1]
        if len(params) == 3:
            try:
                baudrate = int(params[2])
            except ValueError:
                return "Wrong format for baudrate, should be a number", None

        self.plugin._printer.connect(port=port, baudrate=baudrate, profile=None)
        # Sleep a while before checking if connected
        time.sleep(10)
        if not self.plugin._printer.is_operational():
            return 'Failed to connect, try: "/connect [port] [baudrate]"', None

        return 'Connected to printer', None

    def disconnect(self):
        if not self.plugin._printer.is_operational():
            return 'Printer is not connected', None
        self.plugin._printer.disconnect()
        # Sleep a while before checking if disconnected
        time.sleep(10)
        if self.plugin._printer.is_operational():
            return 'Failed to disconnect', None

        return 'Disconnected to printer', None

    def status(self):
        data = [['Status', 'Value']]

        ip_addr = self.plugin.get_ip_address()
        if ip_addr != "127.0.0.1":
            data.append(['Local IP', ip_addr])

        data.append(['External IP', self.plugin.get_external_ip_address()])

        operational = self.plugin._printer.is_operational()
        data.append(['Operational', 'Yes' if operational else 'No'])
        current_data = self.plugin._printer.get_current_data()

        if current_data.get('currentZ'):
            data.append(['Current Z', current_data['currentZ']])
        if operational:
            temperatures = self.plugin._printer.get_current_temperatures()
            for heater in temperatures.keys():
                if heater == 'bed':
                    continue
                data.append(['Extruder Temp (%s)' % heater, temperatures[heater]['actual']])
            data.append(['Bed Temp', temperatures['bed']['actual']])

            printing = self.plugin._printer.is_printing()
            data.append(['Printing', 'Yes' if printing else 'No'])
            if printing:
                data.append(['File', current_data['job']['file']['name']])
                completion = current_data['progress']['completion']
                if completion:
                    data.append(['Progress', "%d%%" % completion])

                current_time_val = current_data['progress']['printTime']
                if current_time_val:
                    time_spent = humanfriendly.format_timespan(current_time_val, max_units=2)
                    data.append(['Time Spent', time_spent])
                else:
                    data.append(['Time Spent', 'Unknown'])

                remaining_time_val = current_data['progress']['printTimeLeft']
                if remaining_time_val:
                    time_left = humanfriendly.format_timespan(current_data['progress']['printTimeLeft'], max_units=2)
                    data.append(['Time Remaining', time_left])
                else:
                    data.append(['Time Remaining', 'Unknown'])

        table = Table(data)
        return str(table.table), self.plugin.get_snapshot()

    def pause(self):
        self.plugin._printer.pause_print()
        return "Print paused", self.plugin.get_snapshot()

    def resume(self):
        self.plugin._printer.resume_print()
        return "Print resumed", self.plugin.get_snapshot()

    def upload_file(self, filename, url):
        upload_file = self.plugin._file_manager.path_on_disk('local', filename)

        r = requests.get(url, stream=True)
        with open(upload_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return "File Received: %s\n" % filename
