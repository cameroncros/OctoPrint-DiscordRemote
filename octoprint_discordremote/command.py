import collections
import humanfriendly
import re
import time
import requests

from octoprint.printer import InvalidFileLocation, InvalidFileType

from command_plugins import plugin_list
from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed, info_embed


class Command:
    def __init__(self, plugin):
        assert plugin
        self.plugin = plugin
        self.command_dict = collections.OrderedDict()
        self.command_dict['connect'] = {'cmd': self.connect, 'params': "[port] [baudrate]",
                                        'description': "Connect to a printer."}
        self.command_dict['disconnect'] = {'cmd': self.disconnect, 'description': "Disconnect from a printer."}
        self.command_dict['print'] = {'cmd': self.start_print, 'params': "{filename}", 'description': "Print a file."}
        self.command_dict['files'] = {'cmd': self.list_files,
                                      'description': "List all files and respective download links."}
        self.command_dict['abort'] = {'cmd': self.cancel_print, 'description': "Abort a print."}
        self.command_dict['snapshot'] = {'cmd': self.snapshot, 'description': "Take a snapshot with the camera."}
        self.command_dict['status'] = {'cmd': self.status, 'description': "Get the current printer status."}
        self.command_dict['help'] = {'cmd': self.help, 'description': "Print this help."}
        self.command_dict['pause'] = {'cmd': self.pause, 'description': "Pause current print."}
        self.command_dict['resume'] = {'cmd': self.resume, 'description': "Resume current print."}
        self.command_dict['timelapse'] = {'cmd': self.timelapse,
                                          'description': "List all timelapses and respective download links."}
        self.command_dict['mute'] = {'cmd': self.mute,
                                     'description': "Mute notifications"}
        self.command_dict['unmute'] = {'cmd': self.unmute,
                                       'description': "Unmute notifications"}

        # Load plugins
        for command_plugin in plugin_list:
            command_plugin.setup(self, plugin)

    def parse_command(self, string):
        parts = re.split('\s+', string)

        prefix_len = len(self.plugin.get_settings().get(["prefix"]))
        command = self.command_dict.get(parts[0][prefix_len:])
        if command is None:
            if parts[0][0] == self.plugin.get_settings().get(["prefix"]) or \
                    parts[0].lower() == "help":
                return self.help()
            return None, None

        if command.get('params'):
            return command['cmd'](parts)
        else:
            return command['cmd']()

    def timelapse(self):

        api_key = self.plugin.get_settings().global_get(["api", "key"])
        baseurl = self.plugin.get_settings().get(["baseurl"])
        port = self.plugin.get_port()
        if baseurl is None or baseurl == "":
            baseurl = "%s:%s" % (self.plugin.get_ip_address(), port)
        header = {'X-Api-Key': api_key}

        builder = EmbedBuilder()
        builder.set_title('Files and Details')
        builder.set_author(name=self.plugin.get_printer_name())

        response = requests.get("http://127.0.0.1:%s/api/timelapse" % port, headers=header)
        data = response.json()

        for video in data['files']:
            description = ''
            title = ''
            try:
                title = video['name']
            except:
                pass

            try:
                description += 'Size: %s\n' % video['size']
            except:
                pass

            try:
                description += 'Date of Creation: %s\n' % video['date']
            except:
                pass

            try:
                description += 'Download Path: %s\n' % ("http://" + baseurl + video['url'])
            except:
                pass

            builder.add_field(title=title, text=description)

        return None, builder.get_embeds()

    def help(self):
        builder = EmbedBuilder()
        builder.set_title('Commands, Parameters and Description')
        builder.set_author(self.plugin.get_printer_name())

        for command, details in self.command_dict.items():
            builder.add_field(
                title='%s %s' % (self.plugin.get_settings().get(["prefix"]) + command, details.get('params') or ''),
                text=details.get('description'))

        return None, builder.get_embeds()

    def cancel_print(self):
        self.plugin.get_printer().cancel_print()
        return None, error_embed(author=self.plugin.get_printer_name(),
                                 title='Print aborted')

    def start_print(self, params):
        if len(params) != 2:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Wrong number of arguments',
                                     description='try "%sprint [filename]"' % self.plugin.get_settings().get(
                                         ["prefix"]))
        if not self.plugin.get_printer().is_ready():
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Printer is not ready')

        file = self.find_file(params[1])
        if file is None:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Failed to find the file')

        is_sdcard = (file['location'] == 'sdcard')
        try:
            file_path = self.plugin.get_file_manager().path_on_disk(file['location'], file['path'])
            self.plugin.get_printer().select_file(file_path, is_sdcard, printAfterSelect=True)
        except InvalidFileType:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Invalid file type selected')
        except InvalidFileLocation:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Invalid file location?')
        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='Successfully started print',
                                   description=file['path'])

    def list_files(self):
        port = self.plugin.get_port()
        baseurl = self.plugin.get_settings().get(["baseurl"])
        if baseurl is None or baseurl == "":
            baseurl = "%s:%s" % (self.plugin.get_ip_address(), port)

        builder = EmbedBuilder()
        builder.set_title('Files and Details')
        builder.set_author(name=self.plugin.get_printer_name())
        file_list = self.get_flat_file_list()
        for details in file_list:
            description = ''
            title = ''
            try:
                title = details['path'][1:]
            except:
                pass

            try:
                description += 'Location: %s\n' % details['location']
            except:
                pass

            try:
                estimated_print_time = humanfriendly.format_timespan(details['analysis']['estimatedPrintTime'],
                                                                     max_units=2)
                description += 'Estimated Print Time: %s\n' % estimated_print_time
            except:
                pass

            try:
                average_print_time = humanfriendly.format_timespan(
                    details['statistics']['averagePrintTime']['_default'], max_units=2)
                description += 'Average Print Time: %s\n' % average_print_time
            except:
                pass

            try:
                filament_required = humanfriendly.format_length(
                    details['analysis']['filament']['tool0']['length'] / 1000)
                description += 'Filament Required: %s\n' % filament_required
            except:
                pass

            try:
                url = "http://" + baseurl + "/downloads/files/" + details['location'] + "/" + details['path'][1:]
                description += 'Download Path: %s\n' % url
            except:
                pass

            builder.add_field(title=title, text=description)

        return None, builder.get_embeds()

    def snapshot(self):
        snapshots = self.plugin.get_snapshot()
        if snapshots and len(snapshots) == 1:
            return None, info_embed(author=self.plugin.get_printer_name(),
                                    snapshot=snapshots[0])
        return None, None

    def find_file(self, file_name):
        flat_filelist = self.get_flat_file_list()
        for file in flat_filelist:
            if file_name.upper() in file.get('path').upper():
                return file
        return None

    def get_flat_file_list(self):
        file_list = self.plugin.get_file_manager().list_files(recursive=True)
        flat_filelist = []
        for (location, files) in file_list.items():
            self.flatten_file_list_recursive(flat_filelist, location, files, '')

        return flat_filelist

    def flatten_file_list_recursive(self, file_array, location, files, path):
        for filename, details in files.items():
            if details.get('children') is not None:
                # This is a folder, recurse into it
                self.flatten_file_list_recursive(file_array, location, details['children'], filename)
            else:
                if path == '' or not path.endswith('/'):
                    path += '/'
                details['path'] = path + filename
                details['location'] = location
                file_array.append(details)

    def connect(self, params):
        if len(params) > 3:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Too many parameters',
                                     description='Should be: %sconnect [port] [baudrate]' % self.plugin.get_settings().get(
                                         ["prefix"]))
        if self.plugin.get_printer().is_operational():
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Printer already connected',
                                     description='Disconnect first')

        port = None
        baudrate = None
        if len(params) >= 2:
            port = params[1]
        if len(params) == 3:
            try:
                baudrate = int(params[2])
            except ValueError:
                return None, error_embed(author=self.plugin.get_printer_name(),
                                         title='Wrong format for baudrate',
                                         description='should be a number')

        self.plugin.get_printer().connect(port=port, baudrate=baudrate, profile=None)
        # Sleep a while before checking if connected
        time.sleep(10)
        if not self.plugin.get_printer().is_operational():
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Failed to connect',
                                     description='try: "%sconnect [port] [baudrate]"' % self.plugin.get_settings().get(
                                         ["prefix"]))

        return None, success_embed('Connected to printer')

    def disconnect(self):
        if not self.plugin.get_printer().is_operational():
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Printer is not connected')
        self.plugin.get_printer().disconnect()
        # Sleep a while before checking if disconnected
        time.sleep(10)
        if self.plugin.get_printer().is_operational():
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Failed to disconnect')

        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='Disconnected to printer')

    def status(self):
        builder = EmbedBuilder()
        builder.set_title('Status')
        builder.set_author(name=self.plugin.get_printer_name())

        if self.plugin.get_settings().get(['show_local_ip'], merged=True):
            ip_addr = self.plugin.get_ip_address()
            if ip_addr != '127.0.0.1':
                builder.add_field(title='Local IP', text=ip_addr, inline=True)

        if self.plugin.get_settings().get(['show_external_ip'], merged=True):
            builder.add_field(title='External IP', text=self.plugin.get_external_ip_address(), inline=True)

        operational = self.plugin.get_printer().is_operational()
        builder.add_field(title='Operational', text='Yes' if operational else 'No', inline=True)
        current_data = self.plugin.get_printer().get_current_data()

        if current_data.get('currentZ'):
            builder.add_field(title='Current Z', text=current_data['currentZ'], inline=True)
        if operational:
            temperatures = self.plugin.get_printer().get_current_temperatures()
            for heater in temperatures.keys():
                if heater == 'bed':
                    continue
                builder.add_field(title='Extruder Temp (%s)' % heater, text=temperatures[heater]['actual'], inline=True)

            builder.add_field(title='Bed Temp', text=temperatures['bed']['actual'], inline=True)

            printing = self.plugin.get_printer().is_printing()
            builder.add_field(title='Printing', text='Yes' if printing else 'No', inline=True)
            if printing:
                builder.add_field(title='File', text=current_data['job']['file']['name'], inline=True)
                completion = current_data['progress']['completion']
                if completion:
                    builder.add_field(title='Progress', text='%d%%' % completion, inline=True)

                builder.add_field(title='Time Spent', text=self.plugin.get_print_time_spent(), inline=True)
                builder.add_field(title='Time Remaining', text=self.plugin.get_print_time_remaining(), inline=True)

        snapshots = self.plugin.get_snapshot()
        if snapshots and len(snapshots) == 1:
            builder.set_image(snapshots[0])
        return None, builder.get_embeds()

    def pause(self):
        self.plugin.get_printer().pause_print()
        snapshot = None
        snapshots = self.plugin.get_snapshot()
        if snapshots and len(snapshots) == 1:
            snapshot = snapshots[0]
        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='Print paused', snapshot=snapshot)

    def resume(self):
        self.plugin.get_printer().resume_print()
        snapshot = None
        snapshots = self.plugin.get_snapshot()
        if snapshots and len(snapshots) == 1:
            snapshot = snapshots[0]
        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='Print resumed', snapshot=snapshot)

    def upload_file(self, filename, url):
        upload_file = self.plugin.get_file_manager().path_on_disk('local', filename)

        r = requests.get(url, stream=True)
        with open(upload_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='File Received',
                                   description=filename)

    def mute(self):
        self.plugin.mute()
        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='Notifications Muted')

    def unmute(self):
        self.plugin.unmute()
        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title='Notifications Unmuted')
