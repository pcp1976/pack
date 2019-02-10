from pluggy import PluginManager


class Plugin:
    def config_inject(self, config):
        """
        :param config: app-wide config
        """
        raise NotImplementedError

    def plugin_pm_link(self, pm: PluginManager):
        raise NotImplementedError
