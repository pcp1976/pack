import sys
from sys import argv
import hookspecs
import plugins
import pkgutil
from pluggy import PluginManager
from api.eventsource import Event

pm = PluginManager("pack")


def main(args):
    connect_hooks()
    link()
    pm.hook.config_inject(config=pm.hook.broadcast_config())
    pm.hook.config_item_set(item="eventsource", value={"type": "eventsource_sqlite"})
    pm.hook.create_subscription(stream_name="geoff", subscription_name="test")
    event = Event()
    event.metadata = {}
    event.data = {"hello": "world"}
    event.type = "a test"
    pm.hook.eventsource_handler_register(
        stream_name="geoff", subscription_name="test", event_handler=simple_func
    )
    pm.hook.raise_event(stream_name="geoff", event=event)


def simple_func(a, b, c, d):
    print(f"falsey: {a} {b} {c} {d}")


def connect_hooks():
    for importer, modname, ispkg in pkgutil.walk_packages(path="./hookspecs"):
        if hasattr(sys.modules[modname], "pack_register"):
            sys.modules[modname].pack_register(pm)


def link():
    pm.hook.plugin_pm_link(pm=pm)


if __name__ == "__main__":
    main(argv[1:])
