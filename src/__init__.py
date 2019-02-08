import sys
from sys import argv
import hookspecs
import plugins
import pkgutil
from pluggy import PluginManager

pm = PluginManager("pack")

for importer, modname, ispkg in pkgutil.walk_packages(path="./hookspecs"):
    if hasattr(sys.modules[modname], "pack_register_hs"):
        sys.modules[modname].pack_register_hs(pm)
    if hasattr(sys.modules[modname], "pack_register_im"):
        sys.modules[modname].pack_register_hs(pm)


def main(args):
    pm.hook.inject_config(config=pm.hook.broadcast_config())


if __name__ == "__main__":
    main(argv[1:])
