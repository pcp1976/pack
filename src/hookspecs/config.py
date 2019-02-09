from pluggy import HookspecMarker, PluginManager


hs_config = HookspecMarker("pack")


class ConfigMarkers:
    @hs_config
    def config_inject(self, config):
        """
        :param config: the config to inject
        """
        pass

    @hs_config
    def config_broadcast(self):
        """
        :return:
        """
        pass

    @hs_config
    def config_item_set(self, item, value):
        pass

    @hs_config
    def config_item_get(self, item):
        pass


def pack_register(pm: PluginManager):
    pm.add_hookspecs(ConfigMarkers())
