from pluggy import HookimplMarker, PluginManager

hs_config_impl = HookimplMarker("pack")


class PTwo(object):
    @hs_config_impl
    def config_inject(self, config):
        print(f"{self.__class__}: {config}")


def pack_register(pm: PluginManager):
    pm.register(PTwo())
