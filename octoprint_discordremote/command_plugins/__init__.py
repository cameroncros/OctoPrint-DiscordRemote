from octoprint_discordremote.command_plugins import psu_control, enclosure_control

plugin_list = [
    psu_control.PsuControl()
    enclosure_control.EnclosureControl()
]
