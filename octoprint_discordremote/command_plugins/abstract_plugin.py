from abc import abstractmethod


class AbstractPlugin:
    def __init__(self):
        pass

    @abstractmethod
    def setup(self, command, plugin):
        """
        Function to register commands. Use this to detect and
        register any commands you want to use.
        :param command: An instance of the command class,
        used to register the commands.
        :param plugin: An instance of the base plugin. Used to interact
        with OctoPrint
        :return: None
        """
        pass
