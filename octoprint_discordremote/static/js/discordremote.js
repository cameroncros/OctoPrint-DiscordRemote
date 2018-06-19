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
        self.isConnected = ko.observable(undefined);
        self.discordremote = $("#discordremote_indicator")

        self.onStartup = function () {
            self.isConnected.subscribe(function() {
                self.discordremote.removeClass("connecting").removeClass("disconnected").removeClass("connected");
                self.discordremote.addClass(self.isConnected());
            });
            self.isConnected("connecting")
        }

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "discordremote") {
                return;
            }

            self.isConnected(data.isConnected);
        };

        self.sendTestMessage = function() {
            arg_string = prompt("Command to send?", "/status")
            $.ajax({
                url: API_BASEURL + "plugin/discordremote",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "executeCommand",
                    args: arg_string
                }),
                contentType: "application/json; charset=UTF-8"
            });
        }
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        DiscordRemoteViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ "loginStateViewModel", "settingsViewModel" ],

        // e.g. #settings_plugin_discordremote, #tab_plugin_octorant, ...
        [ "#navbar_plugin_discordremote" ]
    ]);
});
