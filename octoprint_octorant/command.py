import argparse
import re
from terminaltables import AsciiTable as Table


class Command:
	def __init__(self, printer_interface, file_manager):
		assert printer_interface
		assert file_manager
		self.printer_interface = printer_interface
		self.file_manager = file_manager

		self.parser = argparse.ArgumentParser(description="OctoPrint command parser")
		self.parser.add_argument("list", help="List the files")
		self.parser.add_argument("print", help="Print a file")
		self.parser.add_argument("cancel", help="Cancel a running print")

	def parse_command(self, str):
		parts = re.split('\s+', str)
		output = self.parser.parse_args(parts)

		snapshot = None
		message = ""

		if output.list:
			message += "The list of files are:\n"
			for key in self.file_manager.registered_storages:
				message += key + ":\n"
				data = []
				for file in self.file_manager.list_files(key):
					data.append([file])

				table = Table(data)
				message += str(table.table) + "\n"
		elif output.print_:
			pass
		elif output.cancel:
			pass

		return message, snapshot
