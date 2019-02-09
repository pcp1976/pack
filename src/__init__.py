import sys
from sys import argv
import hookspecs
import plugins
import pkgutil
from pluggy import PluginManager

pm = PluginManager("pack")


def main(args):
    connect_hooks()
    link()
    pm.hook.config_inject(config=pm.hook.broadcast_config())
    pm.hook.config_item_set(item="eventsource", value={"type": "eventsource_memory"})


def connect_hooks():
    for importer, modname, ispkg in pkgutil.walk_packages(path="./hookspecs"):
        if hasattr(sys.modules[modname], "pack_register"):
            sys.modules[modname].pack_register(pm)
        # if hasattr(sys.modules[modname], "pack_register_im"):
        #     sys.modules[modname].pack_register_im(pm)


def link():
    pm.hook.plugin_pm_link(pm=pm)


if __name__ == "__main__":
    main(argv[1:])
