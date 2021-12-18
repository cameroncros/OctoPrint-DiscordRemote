from __future__ import unicode_literals

import collections
import os
import urllib
import humanfriendly
import re
import time
import requests
import zipfile
import subprocess

from octoprint.printer import InvalidFileLocation, InvalidFileType

from typing import TYPE_CHECKING, Tuple, List, Optional
from discord.embeds import Embed
from discord.file import File

if TYPE_CHECKING:
    from octoprint_discordremote import DiscordRemotePlugin

from octoprint_discordremote.command_plugins import plugin_list
from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed, info_embed, upload_file


class Command:
    def __init__(self, plugin: 'DiscordRemotePlugin'):
        assert plugin
        self.plugin: 'DiscordRemotePlugin' = plugin
        self.command_dict = collections.OrderedDict()
        self.command_dict['connect'] = {'cmd': self.connect, 'params': "[port] [baudrate]",
                                        'description': "Connect to a printer."}
        self.command_dict['disconnect'] = {'cmd': self.disconnect, 'description': "Disconnect from a printer."}
        self.command_dict['print'] = {'cmd': self.start_print, 'params': "{filename}", 'description': "Print a file."}
        self.command_dict['files'] = {'cmd': self.list_files,
                                      'description': "List all files and respective download links."}
        self.command_dict['unzip'] = {'cmd': self.unzip, 'params': "{filename}",
                                      'description': "Unzip .zip files and .zip.001, .zip.002,... files"}
        self.command_dict['abort'] = {'cmd': self.cancel_print, 'description': "Abort a print."}
        self.command_dict['snapshot'] = {'cmd': self.snapshot, 'description': "Take a snapshot with the camera."}
        self.command_dict['status'] = {'cmd': self.status, 'description': "Get the current printer status."}
        self.command_dict['help'] = {'cmd': self.help, 'description': "Print this help."}
        self.command_dict['pause'] = {'cmd': self.pause, 'description': "Pause current print."}
        self.command_dict['resume'] = {'cmd': self.resume, 'description': "Resume current print."}
        self.command_dict['timelapse'] = {'cmd': self.timelapse,
                                          'description': "List all timelapses and respective download links."}
        self.command_dict['mute'] = {'cmd': self.mute,
                                     'description': "Mute notifications."}
        self.command_dict['unmute'] = {'cmd': self.unmute,
                                       'description': "Unmute notifications."}
        self.command_dict['gcode'] = {'cmd': self.gcode, 'params': '{GCODE}',
                                      'description': "Send a set of GCODE commands directly to the printer. GCODE lines seperated by \';\'"}
        self.command_dict['getfile'] = {'cmd': self.getfile, 'params': "{filename}",
                                        'description': "Get a gcode file and upload to discord."}
        self.command_dict['gettimelapse'] = {'cmd': self.gettimelapse, 'params': "{filename}",
                                             'description': "Get a timelapse file and upload to discord."}

        # Load plugins
        for command_plugin in plugin_list:
            command_plugin.setup(self, plugin)

    def parse_command(self, string, user=None) -> List[Tuple[Embed, File]]:
        prefix_str = self.plugin.get_settings().get(["prefix"])
        prefix_len = len(prefix_str)

        parts = re.split(r'\s+', string)

        if len(parts[0]) < prefix_len or prefix_str != parts[0][:prefix_len]:
            return []

        command_string = parts[0][prefix_len:]

        command = self.command_dict.get(command_string, {'cmd': self.help})

        if user and not self.check_perms(command_string, user):
            return error_embed(author=self.plugin.get_printer_name(),
                               title="Permission Denied")

        if command.get('params'):
            return command['cmd'](parts)
        else:
            return command['cmd']()

    def timelapse(self):
        path = os.path.join(os.getcwd(), self.plugin._data_folder, '..', '..', 'timelapse')
        path = os.path.abspath(path)

        builder = EmbedBuilder()
        builder.set_title('Files and Details')
        builder.set_description('Download with /gettimelapse {filename}')
        builder.set_author(name=self.plugin.get_printer_name())

        baseurl = self.plugin.get_settings().get(["baseurl"])
        port = self.plugin.get_port()
        if baseurl is None or baseurl == "":
            baseurl = "%s:%s" % (self.plugin.get_ip_address(), port)

        for root, dirs, files in os.walk(path):
            for name in files:
                try:
                    file_path = os.path.join(root, name)

                    title = os.path.basename(file_path)

                    description = ''
                    description += 'Size: %s\n' % os.path.getsize(file_path)
                    description += 'Date of Creation: %s\n' % time.ctime(os.path.getctime(file_path))
                    description += 'Download Path: %s\n' % \
                                   ("http://" + baseurl + "/downloads/timelapse/" + urllib.parse.quote(title))

                    builder.add_field(title=title, text=description)
                except Exception as e:
                    pass

        return builder.get_embeds()

    def help(self):
        builder = EmbedBuilder()
        builder.set_title('Commands, Parameters and Description')
        builder.set_author(self.plugin.get_printer_name())

        for command, details in self.command_dict.items():
            builder.add_field(
                title='%s %s' % (self.plugin.get_settings().get(["prefix"]) + command, details.get('params') or ''),
                text=details.get('description'))

        return builder.get_embeds()

    def cancel_print(self):
        self.plugin.get_printer().cancel_print()
        return error_embed(author=self.plugin.get_printer_name(),
                           title='Print aborted')

    def start_print(self, params):
        if len(params) != 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of arguments',
                               description='try "%sprint [filename]"' % self.plugin.get_settings().get(
                                   ["prefix"]))
        if not self.plugin.get_printer().is_ready():
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Printer is not ready')

        file = self.find_file(params[1])
        if file is None:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Failed to find the file')

        is_sdcard = (file['location'] == 'sdcard')
        try:
            file_path = self.plugin.get_file_manager().path_on_disk(file['location'], file['path'])
            self.plugin.get_printer().select_file(file_path, is_sdcard, printAfterSelect=True)
        except InvalidFileType:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Invalid file type selected')
        except InvalidFileLocation:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Invalid file location?')
        return success_embed(author=self.plugin.get_printer_name(),
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
                title = details['path'].lstrip('/')
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
                url = "http://" + baseurl + "/downloads/files/" + details['location'] + "/" + details['path'].lstrip(
                    '/')
                description += 'Download Path: %s\n' % url
            except:
                pass

            builder.add_field(title=title, text=description)

        return builder.get_embeds()

    def snapshot(self):
        snapshot = self.plugin.get_snapshot()
        if snapshot:
            return info_embed(author=self.plugin.get_printer_name(),
                              snapshot=snapshot)
        return None

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
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Too many parameters',
                               description='Should be: %sconnect [port] [baudrate]' % self.plugin.get_settings().get(
                                   ["prefix"]))
        if self.plugin.get_printer().is_operational():
            return error_embed(author=self.plugin.get_printer_name(),
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
                return error_embed(author=self.plugin.get_printer_name(),
                                   title='Wrong format for baudrate',
                                   description='should be a number')

        self.plugin.get_printer().connect(port=port, baudrate=baudrate, profile=None)

        # Check every second for 30 seconds, to see if it has connected.
        for i in range(30):
            time.sleep(1)
            if self.plugin.get_printer().is_operational():
                return success_embed('Connected to printer')

        return error_embed(author=self.plugin.get_printer_name(),
                           title='Failed to connect',
                           description='try: "%sconnect [port] [baudrate]"' % self.plugin.get_settings().get(
                               ["prefix"]))

    def disconnect(self):
        if not self.plugin.get_printer().is_operational():
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Printer is not connected')
        self.plugin.get_printer().disconnect()
        # Sleep a while before checking if disconnected
        time.sleep(10)
        if self.plugin.get_printer().is_operational():
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Failed to disconnect')

        return success_embed(author=self.plugin.get_printer_name(),
                             title='Disconnected from printer')

    def status(self):
        builder = EmbedBuilder()
        builder.set_title('Current Status')
        builder.set_author(name=self.plugin.get_printer_name())

        if self.plugin.get_settings().get(['show_local_ip'], merged=True) != 'off':
            ip_addr = self.plugin.get_ip_address()
            if ip_addr != '127.0.0.1':
                builder.add_field(title='Local IP', text=ip_addr, inline=True)

        if self.plugin.get_settings().get(['show_external_ip'], merged=True) != 'off':
            builder.add_field(title='External IP', text=self.plugin.get_external_ip_address(), inline=True)

        operational = self.plugin.get_printer().is_operational()
        builder.add_field(title='Operational', text='Yes' if operational else 'No', inline=True)
        current_data = self.plugin.get_printer().get_current_data()

        if current_data.get('currentZ'):
            builder.add_field(title='Current Z', text=str(current_data['currentZ']), inline=True)
        if operational:
            temperatures = self.plugin.get_printer().get_current_temperatures()
            for heater in temperatures.keys():
                if heater == 'bed':
                    continue
                if temperatures[heater]['actual'] is None or len(str(temperatures[heater]['actual'])) == 0:
                    continue
                builder.add_field(title='Extruder Temp (%s)' % heater,
                                  text=str(temperatures[heater]['actual']),
                                  inline=True)

            if temperatures['bed']['actual']:
                builder.add_field(title='Bed Temp', text=str(temperatures['bed']['actual']), inline=True)

            printing = self.plugin.get_printer().is_printing()
            builder.add_field(title='Printing', text='Yes' if printing else 'No', inline=True)
            if printing:
                builder.add_field(title='File', text=str(current_data['job']['file']['name']), inline=True)
                completion = current_data['progress']['completion']
                if completion:
                    builder.add_field(title='Progress', text='%d%%' % completion, inline=True)

                builder.add_field(title='Time Spent', text=self.plugin.get_print_time_spent(), inline=True)
                builder.add_field(title='Time Remaining', text=self.plugin.get_print_time_remaining(), inline=True)
                builder.add_field(title='ETA', text=self.plugin.get_print_eta(), inline=True)

        try:
            cmd_response = subprocess.Popen(['vcgencmd', 'get_throttled'], stdout=subprocess.PIPE).communicate()
            throttled_string = cmd_response[0].decode().split('=')[1].strip()
            throttled_value = int(throttled_string, 0)
            if throttled_value & (1 << 0):
                builder.add_field(title='WARNING', text="PI is under-voltage", inline=True)
            if throttled_value & (1 << 1):
                builder.add_field(title='WARNING', text="PI has capped it's ARM frequency", inline=True)
            if throttled_value & (1 << 2):
                builder.add_field(title='WARNING', text="PI is currently throttled", inline=True)
            if throttled_value & (1 << 3):
                builder.add_field(title='WARNING', text="PI has reached temperature limit", inline=True)
            if throttled_value & (1 << 16):
                builder.add_field(title='WARNING', text="PI Under-voltage has occurred", inline=True)
            if throttled_value & (1 << 17):
                builder.add_field(title='WARNING', text="PI ARM frequency capped has occurred", inline=True)
            if throttled_value & (1 << 18):
                builder.add_field(title='WARNING', text="PI Throttling has occurred", inline=True)
            if throttled_value & (1 << 19):
                builder.add_field(title='WARNING', text="PI temperature limit has occurred", inline=True)
        except OSError as e:
            pass

        snapshot = self.plugin.get_snapshot()
        if snapshot:
            builder.set_image(snapshot)
        return builder.get_embeds()

    def pause(self):
        self.plugin.get_printer().pause_print()
        snapshot = self.plugin.get_snapshot()
        return success_embed(author=self.plugin.get_printer_name(),
                             title='Print paused', snapshot=snapshot)

    def resume(self):
        self.plugin.get_printer().resume_print()
        snapshot = self.plugin.get_snapshot()
        return success_embed(author=self.plugin.get_printer_name(),
                             title='Print resumed', snapshot=snapshot)

    def download_file(self, filename, url, user):
        if user and not self.check_perms('upload', user):
            return error_embed(author=self.plugin.get_printer_name(),
                               title="Permission Denied")
        upload_file_path = self.plugin.get_file_manager().path_on_disk('local', filename)

        r = requests.get(url, stream=True)
        with open(upload_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return success_embed(author=self.plugin.get_printer_name(),
                             title='File Received',
                             description=filename)

    def unzip(self, params):
        if len(params) != 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of arguments',
                               description='try "%sunzip [filename]"' % self.plugin.get_settings().get(
                                   ["prefix"]))

        file_name = params[1]

        flat_filelist = self.get_flat_file_list()

        unzippable = None

        if file_name.endswith('.zip'):
            for file in flat_filelist:
                if file_name.upper() in file.get('path').upper():
                    unzippable = self.plugin.get_file_manager().path_on_disk(file.get('location'), file_name)
                    break

        elif file_name.endswith('.zip.001'):
            files = []
            truncated = file_name[:-3]
            current = 1
            found = True
            while found:
                found = False
                fn = truncated + str(current).zfill(3)
                for file in flat_filelist:
                    if fn.upper() in file.get('path').upper():
                        files.append(fn)
                        current += 1
                        found = True
                        break
            upload_file_path = self.plugin.get_file_manager().path_on_disk('local', truncated[:-1])
            if self.plugin.get_file_manager().file_exists('local', upload_file_path.rpartition('/')[2]):
                self.plugin.get_file_manager().remove_file('local', upload_file_path.rpartition('/')[2])
            with open(upload_file_path, 'ab') as combined:
                for f in files:
                    path = self.plugin.get_file_manager().path_on_disk('local', f)
                    with open(path, 'rb') as temp:
                        combined.write(temp.read())
                    self.plugin.get_file_manager().remove_file('local', f.rpartition('/')[2])

            unzippable = upload_file_path

        else:
            return error_embed(author=self.plugin.get_printer_name(), title="Not a valid Zip file.",
                               description='try "%sunzip [filename].zip or %sunzip [filename].zip.001 for multi-volume files."' % (
                                   self.plugin.get_settings().get(
                                       ["prefix"]), self.plugin.get_settings().get(
                                       ["prefix"])))

        if unzippable == None:
            return error_embed(author=self.plugin.get_printer_name(), title="File %s not found." % file_name)

        try:
            with zipfile.ZipFile(unzippable) as zip:

                fileOK = zip.testzip()

                if fileOK is not None:
                    return error_embed(author=self.plugin.get_printer_name(), title="Bad zip file.",
                                       description='In case of multi-volume files, one could be missing.')

                availablefiles = zip.namelist()
                filestounpack = []
                for f in availablefiles:
                    if f.endswith('.gcode'):
                        filestounpack.append(f)

                path = unzippable.rpartition('/')[0] + '/'

                for f in filestounpack:
                    with open(path + f, 'wb') as file:
                        with zip.open(f) as source:
                            file.write(source.read())

                self.plugin.get_file_manager().remove_file('local', unzippable.rpartition('/')[2])

        except:
            return error_embed(author=self.plugin.get_printer_name(), title="Bad zip file.",
                               description='In case of multi-volume files, one could be missing.')

        return success_embed(author=self.plugin.get_printer_name(), title='File(s) unzipped. ',
                             description=str(filestounpack))

    def mute(self):
        self.plugin.mute()
        return success_embed(author=self.plugin.get_printer_name(),
                             title='Notifications Muted')

    def unmute(self):
        self.plugin.unmute()
        return success_embed(author=self.plugin.get_printer_name(),
                             title='Notifications Unmuted')

    @staticmethod
    def _parse_array(string: str) -> Optional[List[str]]:
        # noinspection PyBroadException
        try:
            return re.split("[^a-zA-Z0-9*]+", string)
        except:
            return None

    def check_perms(self, command: str, user: int) -> bool:
        permissions = self.plugin.get_settings().get(['permissions'], merged=True)

        for rulename in permissions:
            rule = permissions.get(rulename)
            users = self._parse_array(rule['users'])
            commands = self._parse_array(rule['commands'])
            if users is None or commands is None:
                continue
            if ('*' in users or str(user) in users) and \
                    ('*' in commands or command in commands):
                return True
        return False

    def gcode(self, params):
        if not self.plugin.get_printer().is_operational():
            return error_embed(author=self.plugin.get_printer_name(),
                               title="Printer not connected",
                               description="Connect to printer first.")

        allowed_gcodes = self.plugin.get_settings().get(["allowed_gcode"])
        allowed_gcodes = re.split('[^0-9a-zA-Z]+', allowed_gcodes.upper())
        script = "".join(params[1:]).upper()
        lines = script.split(';')
        for line in lines:
            first = line.strip().replace(' ', '').replace('\t', '')
            first = re.findall('^[a-zA-Z]+[0-9]+', first)
            if first is None or \
                    len(first) == 0 or \
                    first[0] not in allowed_gcodes:
                return error_embed(author=self.plugin.get_printer_name(),
                                   title="Invalid GCODE",
                                   description="If you want to use \"%s\", add it to the allowed GCODEs" % line)
        try:
            self.plugin.get_printer().commands(lines)
        except Exception as e:
            return error_embed(author=self.plugin.get_printer_name(),
                               title="Failed to execute gcode",
                               description="Error: %s" % e)

        return success_embed(author=self.plugin.get_printer_name(),
                             title="Sent script")

    def getfile(self, params):
        filename = " ".join(params[1:])
        foundfile = self.find_file(filename)
        if foundfile is None:
            return error_embed(author=self.plugin.get_printer_name(),
                               title="Failed to find file matching the name given")
        file_path = self.plugin.get_file_manager().path_on_disk(foundfile['location'], foundfile['path'])

        return upload_file(file_path)

    def gettimelapse(self, params):
        filename = " ".join(params[1:]).upper()
        path = os.path.join(os.getcwd(), self.plugin._data_folder, '..', '..', 'timelapse')
        path = os.path.abspath(path)

        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)
                if filename in file_path.upper():
                    return upload_file(file_path)

        return error_embed(author=self.plugin.get_printer_name(),
                           title="Failed to find file matching the name given")
