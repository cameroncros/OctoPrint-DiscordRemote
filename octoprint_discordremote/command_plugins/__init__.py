from octoprint_discordremote.command_plugins import psu_control, enclosure_control, system_commands

plugin_list = [
    psu_control.PsuControl(),
    enclosure_control.EnclosureControl(),
    system_commands.SystemCommands()
]
