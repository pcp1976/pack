from pluggy import HookspecMarker, PluginManager


hs_plugin = HookspecMarker("pack")


class PluginMarkers:
    @hs_plugin
    def plugin_pm_link(self, pm: PluginManager):
        """
        :param pm: the config to inject
        """
        pass

    @hs_plugin
    def plugin_deregister(self, plugin):
        """
        Allow a plugin to deregister
        :param plugin: the plugin we want deregistered.
        """


def pack_register(pm: PluginManager):
    pm.add_hookspecs(PluginMarkers())
