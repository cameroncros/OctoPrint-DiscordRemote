/*
 * View model for OctoPrint-Octorant
 *
 * Author: Benjamin Chanudet
 * License: MIT
 */
$(function() {
    function OctorantViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        OctorantViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ "loginStateViewModel", "settingsViewModel" ],

        // e.g. #settings_plugin_octorant, #tab_plugin_octorant, ...
        [ /* ... */ ]
    ]);
});
