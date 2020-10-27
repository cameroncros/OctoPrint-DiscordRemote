from __future__ import unicode_literals

import collections
import os
import urllib
import humanfriendly
import re
import time
import requests
import subprocess

from octoprint.printer import InvalidFileLocation, InvalidFileType

from octoprint_discordremote.command_plugins import plugin_list
from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed, info_embed, upload_file





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

    def parse_command(self, string, user=None):
        prefix_str = self.plugin.get_settings().get(["prefix"])
        prefix_len = len(prefix_str)

        parts = re.split(r'\s+', string)

        if len(parts[0]) < prefix_len or prefix_str != parts[0][:prefix_len]:
            return None, None

        command_string = parts[0][prefix_len:]

        command = self.command_dict.get(command_string, {'cmd': self.help})

        if user and not self.check_perms(command_string, user):
            return None, error_embed(author=self.plugin.get_printer_name(),
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
                    description += 'Download Path: %s\n' %\
                                   ("http://" + baseurl + "/downloads/timelapse/" + urllib.quote(title))

                    builder.add_field(title=title, text=description)
                except Exception as e:
                    pass

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
                url = "http://" + baseurl + "/downloads/files/" + details['location'] + "/" + details['path'].lstrip('/')
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

        # Check every second for 30 seconds, to see if it has connected.
        for i in range(30):
            time.sleep(1)
            if self.plugin.get_printer().is_operational():
                return None, success_embed('Connected to printer')

        return None, error_embed(author=self.plugin.get_printer_name(),
                                 title='Failed to connect',
                                 description='try: "%sconnect [port] [baudrate]"' % self.plugin.get_settings().get(
                                     ["prefix"]))

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
                builder.add_field(title='File', text=current_data['job']['file']['name'], inline=True)
                completion = current_data['progress']['completion']
                if completion:
                    builder.add_field(title='Progress', text='%d%%' % completion, inline=True)

                builder.add_field(title='Time Spent', text=self.plugin.get_print_time_spent(), inline=True)
                builder.add_field(title='Time Remaining', text=self.plugin.get_print_time_remaining(), inline=True)
        
        #get throttled for pi
        try:
            sb2 = subprocess.Popen(['vcgencmd', 'get_throttled'], stdout=subprocess.PIPE)
            cmd_out2 = sb2.communicate()
            string_value2 = cmd_out2[0].decode().split('=')
            result2 = int(string_value2[1].strip(), 0)
        catch FileNotFoundError:
            pass
        if result2==0: 
            builder.add_field(title='WARNING', text="OCTOPI is under-voltage", inline=True)
        if result2==1: 
            builder.add_field(title='WARNING', text="OCTOPI has capped it's arm frequency ", inline=True)
        if result2==2: 
            builder.add_field(title='WARNING', text="OCTOPI is currently throttled", inline=True)
        if result2==6:
            builder.add_field(title='WARNING', text="under-voltage has occurred", inline=True)
        if result2==17:
            builder.add_field(title='WARNING', text="arm frequency capped has occurred", inline =True)
        if result2==18:
            builder.add_field(title='WARNING', text="throttling has occurred", inline = True)
            
                    

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

    def download_file(self, filename, url, user):
        if user and not self.check_perms('upload', user):
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title="Permission Denied")
        upload_file_path = self.plugin.get_file_manager().path_on_disk('local', filename)

        r = requests.get(url, stream=True)
        with open(upload_file_path, 'wb') as f:
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

    @staticmethod
    def _parse_array(string):
        # noinspection PyBroadException
        try:
            return re.split("[^a-zA-Z0-9*]+", string)
        except:
            return None

    def check_perms(self, command, user):
        permissions = self.plugin.get_settings().get(['permissions'], merged=True)

        for rulename in permissions:
            rule = permissions.get(rulename)
            users = self._parse_array(rule['users'])
            commands = self._parse_array(rule['commands'])
            if users is None or commands is None:
                continue
            if ('*' in users or user in users) and \
               ('*' in commands or command in commands):
                return True
        return False

    def gcode(self, params):
        if not self.plugin.get_printer().is_operational():
            return None, error_embed(author=self.plugin.get_printer_name(),
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
                return None, error_embed(author=self.plugin.get_printer_name(),
                                         title="Invalid GCODE",
                                         description="If you want to use \"%s\", add it to the allowed GCODEs" % line)
        try:
            self.plugin.get_printer().commands(lines)
        except Exception as e:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title="Failed to execute gcode",
                                     description="Error: %s" % e)

        return None, success_embed(author=self.plugin.get_printer_name(),
                                   title="Sent script")

    def getfile(self, params):
        filename = " ".join(params[1:])
        foundfile = self.find_file(filename)
        if foundfile is None:
            return None, error_embed(author=self.plugin.get_printer_name(),
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

        return None, error_embed(author=self.plugin.get_printer_name(),
                                 title="Failed to find file matching the name given")
