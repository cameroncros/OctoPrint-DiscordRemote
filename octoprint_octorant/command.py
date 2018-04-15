import argparse
import re


def parse_command(str):
	parts = re.split('\s+', str)
	parser = argparse.ArgumentParser(description="OctoPrint command parser")
	parser.add_argument("list", help="List the files")
	parser.add_argument("print", help="Print a file")
	parser.add_argument("cancel", help="Cancel a running print")
	output = parser.parse_args(parts)

	if output.list:
		pass
	elif output.print_:
		pass
	elif output.cancel:
		pass
