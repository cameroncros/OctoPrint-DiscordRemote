from unittest import TestCase

import mock

from octoprint_octorant import Command

file_list = {'local': {u'folder1': {'name': u'folder1', 'path': u'folder1', 'size': 6530L, 	'type': 'folder',	'typePath': ['folder'], 'display': u'folder1',
	'children': {
		u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
						'typePath': ['machinecode', 'gcode'], 'analysis': {
				'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
								 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
				'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822075,
						'path': u'folder1/test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
						'size': 6530L}
	}},
	u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
					'typePath': ['machinecode', 'gcode'], 'analysis': {
			'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
							 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
			'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822021,
					'path': u'test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
					'size': 6530L}}}

flatten_file_list = [{'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'test.gcode', 'date': 1525822075, 'path': u'folder1/test.gcode', 'size': 6530L, 'type': 'machinecode', 'typePath': ['machinecode', 'gcode'], 'analysis': {'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None, 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0}, 'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'display': u'test.gcode'},
					 			 {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'test.gcode', 'date': 1525822021, 'path': u'/test.gcode', 'size': 6530L, 'type': 'machinecode', 'typePath': ['machinecode', 'gcode'], 'analysis': {'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None, 'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0}, 'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'display': u'test.gcode'}]

class TestCommand(TestCase):
	_file_manager = mock.Mock()
	_printer = mock.Mock()

	def setUp(self):
		self.command = Command(self)

	def test_parse_command_list(self):
		# Success
		self._file_manager.list_files = mock.Mock()
		self._file_manager.list_files.return_value = file_list
		message, snapshot = self.command.parse_command("/files")
		self._file_manager.list_files.assert_called_once()
		self.assertIn("List of files", message)
		self.assertIsNone(snapshot)

	def test_parse_command_print(self):
		# FAIL: Printer not ready
		self._printer.is_ready = mock.Mock()
		self._printer.is_ready.return_value = False
		message, snapshot = self.command.parse_command("/print test.gcode")
		self._printer.is_ready.assert_called_once()
		self.assertEqual("Printer is not ready", message)
		self.assertIsNone(snapshot)
		#TODO

		# Success: Printer ready
		#TODO: Mock and validate the print started
		self.command.get_flat_file_list = mock.Mock()
		self.command.get_flat_file_list.return_value = flatten_file_list
		self._printer.is_ready = mock.Mock()
		self._printer.is_ready.return_value = True
		message, snapshot = self.command.parse_command("/print test.gcode")
		self._printer.is_ready.assert_called_once()
		self.assertIn("Successfully started print:", message)
		self.assertIn("test.gcode", message)
		self.assertIsNone(snapshot)

	def get_snapshot(self):
		"""Mock snapshot function."""
		return open("unittests/test_pattern.png")

	def test_parse_command_snapshot(self):
		# Fail: Camera not working.
		#TODO

		# Success: Camera serving images
		TestCommand.get_snapshot = mock.Mock()
		with open("unittests/test_pattern.png") as input_file:
			TestCommand.get_snapshot.return_value = input_file

			message, snapshot = self.command.parse_command("/snapshot")

			self.assertIsNone(message)
			with open("unittests/test_pattern.png") as image:
				self.assertEqual([image.read()], [snapshot.read()])

	def test_parse_command_abort(self):
		# Fail: No print running
		#TODO

		# Success: Print aborted
		#TODO mock and validate
		message, snapshot = self.command.parse_command("/abort")
		self.assertEqual("Print aborted", message)
		self.assertIsNone(snapshot)

	def test_parse_command_help(self):
		# Success: Printed help
		message, snapshot = self.command.parse_command("/help")
		self.assertIn("List of commands", message)
		for command, details in self.command.command_dict.items():
			self.assertIn(command, message)
			if details.get('params'):
				self.assertIn(details.get('params'), message)
			self.assertIn(details.get('description'), message)
		self.assertIsNone(snapshot)

	def test_get_flat_file_list(self):
		self._file_manager.list_files = mock.Mock()
		self._file_manager.list_files.return_value = file_list
		flat_file_list = self.command.get_flat_file_list()
		self._file_manager.list_files.assert_called_once()
		self.assertEqual(2, len(flat_file_list))
		self.assertEqual(flatten_file_list, flat_file_list)

	@mock.patch("time.sleep")
	def test_parse_command_connect(self, mock_sleep):
		# Fail: Too many parameters
		message, snapshot = self.command.parse_command("/connect asdf asdf  asdf")
		self.assertEqual("Too many parameters. Should be: /connect [port] [baudrate]", message)
		self.assertIsNone(snapshot)

		# Fail: Printer already connected
		self._printer.is_operational = mock.Mock()
		self._printer.is_operational.return_value = True
		message, snapshot = self.command.parse_command("/connect")
		self.assertEqual('Printer already connected. Disconnect first', message)
		self.assertIsNone(snapshot)
		self._printer.is_operational.assert_called_once()

		# Fail: wrong format for baudrate
		self._printer.is_operational = mock.Mock()
		self._printer.is_operational.return_value = False
		message, snapshot = self.command.parse_command("/connect port baudrate")
		self.assertEqual('Wrong format for baudrate, should be a number', message)
		self.assertIsNone(snapshot)
		self._printer.is_operational.assert_called_once()

		# Fail: connect failed.
		self._printer.is_operational = mock.Mock()
		self._printer.is_operational.return_value = False
		self._printer.connect = mock.Mock()
		message, snapshot = self.command.parse_command("/connect port 1234")
		self.assertEqual('Failed to connect, try: "/connect [port] [baudrate]"', message)
		self.assertIsNone(snapshot)
		self.assertEqual(2, self._printer.is_operational.call_count)
		self._printer.connect.assert_called_once_with(port="port", baudrate=1234, profile=None)

	@mock.patch("time.sleep")
	def test_parse_command_disconnect(self, mock_sleep):
		# Fail: Printer already disconnected
		self._printer.is_operational = mock.Mock()
		self._printer.is_operational.return_value = False
		message, snapshot = self.command.parse_command("/disconnect")
		self.assertEqual('Printer is not connected', message)
		self.assertIsNone(snapshot)
		self._printer.is_operational.assert_called_once()

		# Fail: disconnect failed.
		self._printer.is_operational = mock.Mock()
		self._printer.is_operational.return_value = True
		self._printer.disconnect = mock.Mock()
		message, snapshot = self.command.parse_command("/disconnect")
		self.assertEqual('Failed to disconnect', message)
		self.assertIsNone(snapshot)
		self.assertEqual(2, self._printer.is_operational.call_count)
		self._printer.disconnect.assert_called_once_with()
