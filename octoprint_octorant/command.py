import re
from terminaltables import AsciiTable as Table


class Command:
	def __init__(self, plugin):
		assert plugin
		self.plugin = plugin

	def parse_command(self, string):
		parts = re.split('\s+', string)

		snapshot = None
		message = ""

		if parts[0].upper() == "list".upper():
			message += "The list of files are:\n"
			file_list = self.plugin._file_manager.list_files()
			data = [["File Name",
			         "Extimated Print Time",
				 "Average Print Time",
			         "Filament Required"]]
			for (location, files) in file_list.items():
				for (filename, details) in files.items():
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

					data.append([filename,
					             estimated_print_time,
					             average_print_time,
					             filament_required
					             ])
				table = Table(data)
				message += str(table.table)
		elif parts[0].upper() == "print".upper():
			pass
		elif parts[0].upper() == "cancel".upper():
			self._plugin.printer.cancel_print()
			message = ""
		else:
			message = "Help:\n" \
			          "* list - List all files\n" \
			          "* print [filename] - Print a file\n" \
			          "* cancel - Cancel a print"

		return message, snapshot
