from pluggy import HookimplMarker, PluginManager
from dotenv import load_dotenv
import dotenv
import os

load_dotenv()
hs_config_impl = HookimplMarker("pack")


class EnvConfig(object):
    os_environ = os.environ

    @hs_config_impl
    def broadcast_config(self):
        return dotenv.dotenv_values()


def pack_register_hs(pm: PluginManager):
    pm.register(EnvConfig())
