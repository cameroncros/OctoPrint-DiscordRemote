# OctoPrint-DiscordRemote

DiscordRemote is a plugin allowing Octoprint to send notifications to a Discord channel.
The plugin connects to a [DiscordShim](https://github.com/cameroncros/discordshim_rs)
which manages the actual discord interactions.

There is an existing DiscordShim that is already setup, or users may create and use their own DiscordShim instance.

This is forked from  https://github.com/bchanudet/OctoPrint-Octorant.

Note, using this plug-in requires either:

- Adding the existing discordshim bot to your server:
  - https://discord.com/oauth2/authorize?client_id=433252064324354048&permissions=11264&scope=bot
or
- Self host your own discordshim:
  - https://github.com/cameroncros/discordshim_rs

License : MIT

## Credits

[Benjamin Chanudet](https://github.com/bchanudet) for their initial plugin, which this is based on.

[OctopusProteins](https://github.com/OctopusProteins) for their work on the enclosure plugin, file upload capabilities and presence updates.

[megasaturnv](https://github.com/megasaturnv) for their assistance with configuring the access settings.

[goscicki](https://github.com/goscicki) for their help testing the /gcode capability.

[timothy-b](https://github.com/timothy-b) for their help fixing the help command handling.

[wchill](https://github.com/wchill) for the custom embed in notification change.

[SgtKiLLx](https://github.com/SgtKiLLx) for various typo fixes.

[Zinc-OS](https://github.com/Zinc-OS) for adding Raspberry Pi throttling status to the status message.

[Stwend](https://github.com/Stwend) for adding split zip support, to get around the 8mb discord limit.

[Mary](https://github.com/kijk2869) for preventing the bot replying to other bots, and avoiding downloading non-gcode/zip files.

[Milo Mirate](https://github.com/mmirate) for adding ETA to status.

[jneilliii](https://github.com/jneilliii) for [Print Scheduler](https://plugins.octoprint.org/plugins/printscheduler/) support.

[grantrules](https://github.com/grantrules) for fixing presence.

[Jester](https://discord.com) for assisting with debugging the network issues in v5.0

## Changelog

See [the release history](https://github.com/cameroncros/OctoPrint-DiscordRemote/releases) to get a quick summary of what's new in the latest versions.

## Setup

### Install the plugin

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/cameroncros/OctoPrint-DiscordRemote/archive/master.zip

#### Tips

- The Channel ID is the ID of the TEXT channel within the Discord Server that the bot is communicating with, not the Discord Server.
- If you reinstall your Octoprint system, you only need the channel ID, and DiscordShim address to get it back up and running.

## API

There are currently 2 API's available for interacting with the bot.
These can be used by sending a POST request to `[octoprint_url]/api/plugin/discordremote`, with JSON in the body of the request.

### Send command
This API lets you send a command as if you typed it in discord.
The response will be sent to discord.
The JSON format is:

    {
        "command": "executeCommand",
        "args": "COMMAND GOES HERE"
    }

### Send message
This API lets you send a message directly to discord.
The JSON format is:

    {
        "command": "sendMessage",
        "title": "TITLE GOES HERE",
        "description": "DESCRIPTION GOES HERE",
        "color": 0x123456,
        "image": "BASE64 ENCODED FILE DATA HERE",
        "imagename": "IMAGE NAME GOES HERE"
    }

* All fields are optional, but at least a title, description or image should be provided.
* The color is an integer value here that corresponds to the color you want.
* The image is base64 bytes.
* The image name defaults to "snapshot.png" if not provided.

## Commands

To get a list of available commands and arguments, type ``/help`` into the discord channel. The bot will return all available commands.
Commands can also be sent via the web interface, by clicking the button in the top panel that looks like a game controller.
Files can be uploaded to the discord channel directly, and they will be downloaded into OctoPrint automatically. You can use the `/unzip`
command to manage zip files.

## Configuration

The plugin can be configured in the configuration panel, under the "DiscordRemote" panel.

### Discord Settings

- Channel ID: The ID of a channel the bot will listen and post to.
  Ensure that this is locked down so that strangers cannot send commands to your printer, or whitelist users using the "Access Settings"

In order for you to be sure these settings work, every time you change one of them, a test message will be sent to the corresponding Discord Channel.
If you don't receive it, something is most likely wrong!

### Access Settings

The access settings allow specific commands to be limited to specific users.
* In the commands section, put a comma-separated list of commands.
  * Check out [this wiki page](https://github.com/cameroncros/OctoPrint-DiscordRemote/wiki/Default-Commands,-Parameters-and-Description) for the list of commands
  * The command list should look like "help, status, snapshot, mute, unmute" and is useful for tailoring access to any other users you might invite to avoid them issuing a command like /abort!
* In the users section, put a comma-separated list of user IDs.
  * The user ID needs to be the numerical form, which is a number like: 165259232034275409
  * In a text channel, find a message sent by you (or send one) and then right-click your name over that message and click "Copy ID"
  * Or, join a voice channel, and then right-click your name in the sidebar, and click "Copy ID"
  * The text user ID (like "MyUser" or "MyUser#1234") will result in "Permission Denied" responses to commands.
* A '*' in either section can be used to match all commands/users.

If the current command and user combination matches any of the rules, it will be executed.
If additional rules are required, manually editing the config will be required.

### Message Settings

Here you can customize every message handled by DiscordRemote.

- **Toggle the message** : by unchecking the checkbox in front of the message title, you can disable the message. It won't be sent to Discord.
- **Message** : you can change the default content here. See the section [Message format](#message-format) for more information.
- **Include snapshot** : if you have a snapshot URL defined in the Octoprint settings, you can choose to upload a snapshot with the message to Discord.
- **Notify every `XX`%** : specific to the `printing progress` message, this settings allows you to change the frequency of the notification :
    - `10%` means you'll receive a message at 10%, 20%, 30%, 40% ... 80%, 90% of the printing process.
    - `5%` means you'll receive a message at 5%, 10%, 15%, 20% ... 80%, 85%, 90%, 95% of the printing process.
    - etc...
- **Timeout** : for small prints, prevents discord spam by only sending progress messages after the timeout has passed since the previous message.

## Message format

Messages are regular Discord messages, which means you can use :
- `**markdown**` format (see [Discord Documentation](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-))
- `:emoji:` shortcuts to display emojis
- `@mentions` to notify someone

Some events also support variables, here is a basic list :
**Common** :
- `{ipaddr}` : the internal IP address of the OctoPrint server
- `{externaddr}` : the external IP address of the OctoPrint server
- `{timeremaining}` : the time remaining for the print ('Unknown' if the print is not running)
- `{timespent}` : the time spent so far on the print
- `{eta}` : the date+time which is `{timeremaining}` into the future

**Printing process : started event** :
- `{name}` : file's name that's being printed
- `{path}` : file's path within its origin location
- `{origin}` : the origin storage location

**Printing process : failed event** :
- `{name}` : file's name that's being printed
- `{path}` : file's path within its origin location
- `{origin}` : the origin storage location

**Printing process : done event** :
- `{name}` : file's name that's being printed
- `{path}` : file's path within its origin location
- `{origin}` : the origin storage location
- `{time}`: time needed for the print (in seconds)
- `{time_formatted}` : same as `{time}`, but in a human-readable format (`HH:MM:SS`)

**Printing process : failed event** :
- `{name}` : file's name that's being printed
- `{path}` : file's path within its origin location
- `{origin}` : the origin storage location
- `{position}`: position of the hotend

**Printing process : paused event** :
- `{name}` : file's name that's being printed
- `{path}` : file's path within its origin location
- `{origin}` : the origin storage location
- `{position}`: position of the hotend

**Printing process : resumed event** :
- `{name}` : file's name that's being printed
- `{path}` : file's path within its origin location
- `{origin}` : the origin storage location
- `{position}`: position of the hotend

**Printing progress event** :
- `{progress}` : progress in % of the print.

**Printer state : error**
- `{error}` : The error received

For more reference, you can go to the [Octoprint documentation on Events](http://docs.octoprint.org/en/master/events/index.html#sec-events-available-events)

## Issues and Help

If you encounter any trouble don't hesitate to [open an issue](https://github.com/cameroncros/OctoPrint-DiscordRemote/issues/new). I'll gladly do my best to help you setup this plugin.
