# OctoPrint-DiscordRemote

DiscordRemote is a plugin allowing Octoprint to send notifications to a Discord channel via a discord bot. It also listens on the channel and can accept commands to control the printer.
This is forked from  https://github.com/bchanudet/OctoPrint-Octorant.

[![](https://circleci.com/gh/cameroncros/OctoPrint-DiscordRemote.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/cameroncros/OctoPrint-DiscordRemote)

License : MIT

## Credits

[Benjamin Chanudet](https://github.com/bchanudet) for their initial plugin, which this is based on.

[OctopusProteins](https://github.com/OctopusProteins) for their work on the enclosure plugin, and file upload capabilities.

## Changelog

See [the release history](https://github.com/cameroncros/OctoPrint-DiscordRemote/releases) to get a quick summary of what's new in the latest versions.

## Setup

### Install the plugin

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/cameroncros/OctoPrint-DiscordRemote/archive/master.zip

### Create the Discord Bot  in Discord

See the following link for instructions on how to setup a Discord bot and get the Channel ID:

    https://github.com/Chikachi/DiscordIntegration/wiki/How-to-get-a-token-and-channel-ID-for-Discord
    
## Commands

To get a list of available commands and arguments, type ``/help`` into the discord channel. The bot will return all available commands.
Commands can also be sent via the web interface, by clicking the button in the top panel that looks like a game controller.

## Configuration

The plugin can be configured in the configuration panel, under the "DiscordRemote" panel.

### Discord Settings

- Bot Token: The token for a discord bot.
- Channel ID: The ID of a channel the bot will listen and post to. Ensure that this is locked down so that strangers cannot send commands to your printer, or whitelist users using the "Allowed Users" setting.
- Allowed Users: A whitelist of the users that are allowed to interact with. The bot will only respond if the users _ID_ (Not user name) is in this list.

In order for you to be sure these settings work, every time you change one of them, a test message will be sent to the corresponding Discord Channel. If you don't receive it, something is most likely wrong!

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
- `**markdown**` format (see [Discord Documentation](https://support.discordapp.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-))
- `:emoji:` shortcuts to display emojis
- `@mentions` to notify someone

Some events also support variables, here is a basic list :

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
