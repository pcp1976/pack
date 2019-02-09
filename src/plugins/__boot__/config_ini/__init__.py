from pluggy import HookimplMarker, PluginManager
from configobj import ConfigObj
import os

hs_config_impl = HookimplMarker("pack")


class EnvConfig:
    configob = ConfigObj(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    )

    @hs_config_impl
    def broadcast_config(self):
        return self.configob.dict()

    @hs_config_impl
    def config_item_set(self, item, value):
        self.configob[item].update(value)
        self.configob.write()

    @hs_config_impl
    def config_item_get(self, item):
        return self.configob[item]


def pack_register(pm: PluginManager):
    pm.register(EnvConfig())
