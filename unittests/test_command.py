from unittest import TestCase

from octoprint_octorant import Command

class MockFileManager(object):
	def list_files(self, recursive=False):
		if recursive:
			return {'local': {u'folder1': {'children': {
				u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
								'typePath': ['machinecode', 'gcode'], 'analysis': {
						'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
										 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
						'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822075,
								'path': u'folder1/test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
								'size': 6530L}}, 'name': u'folder1', 'path': u'folder1', 'size': 6530L,
				'type': 'folder',
				'typePath': ['folder'], 'display': u'folder1'},
				u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
								'typePath': ['machinecode', 'gcode'], 'analysis': {
						'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
										 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
						'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822021,
								'path': u'test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
								'size': 6530L}}}
		else:
			return {'local': {u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
											  'typePath': ['machinecode', 'gcode'], 'analysis': {
					'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
									 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
					'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822021, 'path': u'test.gcode',
											  'type': 'machinecode', 'display': u'test.gcode', 'size': 6530L}}}


class MockPrinter(object):
	pass

class TestCommand(TestCase):
	_file_manager = MockFileManager()
	_printer = MockPrinter()

	def setUp(self):
		self.command = Command(self)

	def test_parse_command_list(self):
		# Success
		message, snapshot = self.command.parse_command("/files")
		self.assertTrue("The list of files are:" in message)
		self.assertIsNone(snapshot)

	def test_parse_command_print(self):
		# FAIL: Printer not ready
		#TODO

		# Success: Printer ready
		#TODO: Mock and validate the print started
		message, snapshot = self.command.parse_command("/print test.gcode")
		self.assertEqual("Print started", message)
		self.assertIsNone(snapshot)

	def test_parse_command_snapshot(self):
		# Fail: Camera not working.
		#TODO

		# Success: Camera serving images
		message, snapshot = self.command.parse_command("/snapshot")
		self.assertIsNone(message)
		with open("unittests/test_pattern.png") as image:
			self.assertEqual(image.read(), snapshot.read())

	def test_parse_command_print(self):
		# Fail: No print running
		#TODO

		# Success: Print aborted
		#TODO mock and validate
		message, snapshot = self.command.parse_command("/abort")
		self.assertEqual("Print aborted", message)
		self.assertIsNone(snapshot)

	def test_parse_command_help(self):
		# Success: Printed help
		message, snapshot = self.command.parse_command("/abort")
		self.assertTrue("Help:" in message)
		self.assertIsNone(snapshot)


