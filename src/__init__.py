import sys
from sys import argv
import pkgutil
from pluggy import PluginManager
from api.eventsource import Event
from time import sleep

# "unused" - lazy instantiation
import hookspecs
import plugins


pm = PluginManager("pack")


def main(args):
    do_boot()

    # all components should now be connected to the event source
    pm.hook.create_subscription(stream_name="geoff", subscription_name="test")
    event = Event()
    event.metadata = {"author": "Paul"}
    event.data = {"hello": "world"}
    event.type = "a test"
    pm.hook.eventsource_handler_register(
        stream_name="geoff", subscription_name="test", event_handler=simple_func
    )
    pm.hook.raise_event(stream_name="geoff", event=event)
    sleep(1)
    pm.hook.raise_event(stream_name="geoff", event=event)
    sleep(1)
    pm.hook.raise_event(stream_name="geoff", event=event)


def do_boot():
    connect_hooks()
    link()
    pm.hook.config_inject(config=pm.hook.broadcast_config())
    event = Event()
    event.metadata = {"author": "Paul"}
    event.data = {}
    event.type = "config_update"
    pm.hook.raise_event(stream_name="command", event=event)


def simple_func(_id, _type, data, metadata, raised_time):
    event = Event(
        _id=_id, type=_type, data=data, metadata=metadata, _raised_time=raised_time
    )
    print(f"simple_func: {event.__dict__}")


def parse_args(args):
    pass


def connect_hooks():
    for importer, modname, ispkg in pkgutil.walk_packages(path="./hookspecs"):
        if hasattr(sys.modules[modname], "pack_register"):
            sys.modules[modname].pack_register(pm)


def link():
    pm.hook.plugin_pm_link(pm=pm)


if __name__ == "__main__":
    main(argv[1:])
