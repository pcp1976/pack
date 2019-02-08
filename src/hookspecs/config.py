from pluggy import HookspecMarker, PluginManager


hs_config = HookspecMarker("pack")


class ConfigMarkers:
    @hs_config
    def inject_config(self, config):
        """
        :param config: the config to inject
        """
        pass

    @hs_config
    def broadcast_config(self):
        """
        :return:
        """
        pass


def pack_register_hs(pm: PluginManager):
    pm.add_hookspecs(ConfigMarkers())
