from pluggy import HookimplMarker, PluginManager
from configobj import ConfigObj
import os

hs_config_impl = HookimplMarker("pack")


class EnvConfig:
    configob = ConfigObj(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))

    @hs_config_impl
    def broadcast_config(self):
        return self.configob.dict()


def pack_register_hs(pm: PluginManager):
    pm.register(EnvConfig())
