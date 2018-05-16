/*
 * View model for OctoPrint-DiscordRemote
 *
 * Author: Benjamin Chanudet
 * License: MIT
 */
$(function() {
    function DiscordRemoteViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        DiscordRemoteViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ "loginStateViewModel", "settingsViewModel" ],

        // e.g. #settings_plugin_discordremote, #tab_plugin_octorant, ...
        [ /* ... */ ]
    ]);
});
