import re

from octoprint.printer import InvalidFileLocation, InvalidFileType
from terminaltables import AsciiTable as Table

class Command:
	def __init__(self, plugin):
		assert plugin
		self.plugin = plugin
		self.command_dict = {
			'/print':    {'cmd': self.start_print, 'param': True},
			'/files':    {'cmd': self.list_files},
			'/abort':    {'cmd': self.cancel_print},
			'/snapshot': {'cmd': self.snapshot},
			'/help' :    {'cmd': self.help}
		}

	def parse_command(self, string):
		parts = re.split('\s+', string)

		command = self.command_dict.get(parts[0])
		if command is None:
			return self.help(), None

		if command.get('param'):
			return command['cmd'](parts)
		else:
			return command['cmd']()

	def help(self):
		message = "Help:\n" \
				  "* list - List all files\n" \
				  "* print [filename] - Print a file\n" \
				  "* cancel - Cancel a print"
		return message, None

	def cancel_print(self):
		if self.plugin._printer.cancel_print():
			return "Print aborted", None
		else:
			return "Failed to abort print, is there a print running?", None

	def start_print(self, args):
		if len(args) != 2:
			return "Wrong number of arguments, try 'print [filename]'", None
		if not self.plugin._printer.is_ready():
			return "Printer is not ready", None

		file = self.find_file(args[1])
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
		message = "The list of files are:\n"
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

		table = Table(data)
		message += str(table.table)
		return message, None

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

