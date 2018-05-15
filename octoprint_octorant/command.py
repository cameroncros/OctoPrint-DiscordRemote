import re
import time

from octoprint.printer import InvalidFileLocation, InvalidFileType
from terminaltables import AsciiTable as Table

class Command:
	def __init__(self, plugin):
		assert plugin
		self.plugin = plugin
		self.command_dict = {
			'/connect': {'cmd': self.connect, 'params': "[port] [baudrate]", 'description': "Connect to a printer"},
			'/disconnect': {'cmd': self.disconnect, 'description': "Disconnect to a printer"},
			'/print':    {'cmd': self.start_print, 'params': "{filename}", 'description': "print a file"},
			'/files':    {'cmd': self.list_files, 'description': "List all the files"},
			'/abort':    {'cmd': self.cancel_print, 'description': "Abort a print"},
			'/snapshot': {'cmd': self.snapshot, 'description': "Take a snapshot with the camera"},
			'/help' :    {'cmd': self.help, 'description': "Print this help"}
		}

	def parse_command(self, string):
		parts = re.split('\s+', string)

		command = self.command_dict.get(parts[0])
		if command is None:
			return self.help(), None

		if command.get('params'):
			return command['cmd'](parts)
		else:
			return command['cmd']()

	def help(self):
		data = [["Command",
				 "Params",
				 "Description"]]

		for command, details in self.command_dict.items():
			data.append([command, details.get('params') or "", details.get('description')])

		table = Table(data, title="List of commands")
		message = str(table.table)
		return message, None

	def cancel_print(self):
		if self.plugin._printer.cancel_print():
			return "Print aborted", None
		else:
			return "Failed to abort print, is there a print running?", None

	def start_print(self, params):
		if len(params) != 2:
			return "Wrong number of arguments, try 'print [filename]'", None
		if not self.plugin._printer.is_ready():
			return "Printer is not ready", None

		file = self.find_file(params[1])
		if file is None:\
			return "Failed to find the file", None

		is_sdcard = (file['location']=='sdcard')
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
		data = [["Storage",
				 "File Path",
				 "Extimated Print Time",
				 "Average Print Time",
				 "Filament Required"]]
		for details in file_list:

			location = ""
			try:
				location = details['location']
			except:
				pass

			file_path = ""
			try:
				file_path = details['path']
			except:
				pass

			estimated_print_time = ""
			try:
				estimated_print_time = details['analysis']['estimatedPrintTime']
			except:
				pass

			average_print_time = ""
			try:
				average_print_time = details['statistics']['averagePrintTime']['_default']
			except:
				pass

			filament_required = ""
			try:
				filament_required = details['analysis']['filament']['tool0']['length']
			except:
				pass

			data.append([
				location,
				file_path,
				estimated_print_time,
				average_print_time,
				filament_required
			])

		table = Table(data, title="List of files")
		return  str(table.table), None

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
		if  self.plugin._printer.is_operational():
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
