from pluggy import HookimplMarker, PluginManager

hs_config_impl = HookimplMarker("pack")


class PTwo(object):

    @hs_config_impl
    def inject_config(self, config):
        print(f"{self.__class__}: {config}")


def pack_register_hs(pm: PluginManager):
    pm.register(PTwo())
