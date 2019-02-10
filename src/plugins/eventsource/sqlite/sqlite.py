from pluggy import HookimplMarker, PluginManager
from configobj import ConfigObj
from sqlite3 import OperationalError
import os

from api.plugin import Plugin
from api.eventsource import Event, EventSource
from .table_adapter import TableAdapter

eventsource = HookimplMarker("pack")


class EventSourceSqlite(EventSource, Plugin):
    """
    Fairly simple persistent event source using sqlite3
    """

    def __init__(self):
        super().__init__()
        self.name = "eventsource_sqlite"
        self.streams = {}
        self.subscriptions = {}
        self.table_adapter: TableAdapter = None

    @eventsource
    def plugin_pm_link(self, pm: PluginManager):
        print(self.create_subscription.__qualname__)
        self.pm = pm

    def _config_mung(self, config) -> dict:
        """
        config is going to be a list, containing... stuff
        probably a list, and a dict - at least initially
        :param config:
        :return: a config object we can use...
        """
        new_config = ConfigObj()
        for config_thing in config:
            new_config.update(config_thing)
        return new_config

    def apply_config(self, config):
        self.config_obj = config
        # TODO apply any relevant settings
        if self.config_obj["eventsource"]["file"] != ":memory:":
            self.table_adapter = TableAdapter(
                os.path.join(os.getcwd(), self.config_obj["eventsource"]["file"])
            )
        else:
            self.table_adapter = TableAdapter(
                self.config_obj["eventsource"]["file"]
            )
        self.table_adapter.create_subscription_table()

    @eventsource
    def config_inject(self, config):
        fresh_config = self._config_mung(config)
        if not fresh_config["eventsource"]["type"] == self.name:
            print(f"{self.name} unwanted; die")
            self.pm.unregister(self)
        else:
            self.apply_config(fresh_config)

    @eventsource
    def eventsource_handler_register(
        self, stream_name, subscription_name, event_handler
    ):
        """
        :param stream_name: name of the stream the event_handler receives events from
        :param subscription_name: identifier for the subscription
        :param event_handler: function which will receive events from the stream
        :return: None
        """
        # need to keep a reference to the stream (table) subscription, and event_handler,
        # in order to remove them at a later time if necessary
        # stream and subscription potentially don't yet exist
        self.create_subscription(stream_name, subscription_name)
        if event_handler not in self.subscriptions[stream_name][subscription_name]:
            self.table_adapter.register_handler(
                stream_name, subscription_name, event_handler
            )
            self.subscriptions[stream_name][subscription_name].append(event_handler)
        # TODO replay past events to new subscriber

    @eventsource
    def deregister_event_handler(self, event_handler):
        """
        :param event_handler: function which will no longer receive events from the stream
        :return: None
        """
        for stream in self.subscriptions:
            for sub in self.subscriptions[stream]:
                if event_handler in self.subscriptions[stream][sub]:
                    self.subscriptions[stream][sub].remove(event_handler)

    @eventsource
    def delete_subscription(self, stream_name, subscription_name):
        """
        :param stream_name: name of the stream to delete the subscription from
        :param subscription_name: identifier of the subscription to delete
        :return: None
        """
        if subscription_name in self.subscriptions[stream_name]:
            self.table_adapter.delete_subscription(subscription_name)
            self.subscriptions[stream_name].remove(subscription_name)

    def create_stream(self, stream_name):
        if stream_name not in self.streams:
            try:
                self.table_adapter.create_stream_table(stream_name)
            except OperationalError as e:
                if str(e).find("already exists") > 0:
                    print(f"stream {stream_name} already exists")
            self.streams.update({stream_name: []})

    @eventsource
    def create_subscription(self, stream_name, subscription_name):
        if stream_name not in self.subscriptions:
            self.create_stream(stream_name)
            self.subscriptions.update({stream_name: {}})
        if subscription_name not in self.subscriptions[stream_name]:
            self.table_adapter.create_subscription(stream_name, subscription_name)
            self.subscriptions[stream_name].update({subscription_name: []})

    @eventsource
    def raise_event(self, stream_name: str, event: Event):
        self.create_stream(stream_name)  # ensure stream exists
        self.table_adapter.append_event(stream_name, event)

    @eventsource
    def start_event_streams(self) -> bool:
        """
        Start up the event streams
        :return: bool True on success
        """
        pass

    @eventsource
    def stop_event_streams(self) -> bool:
        """
        Stop event streams
        :return: bool True on success
        """
        pass


def pack_register(pm: PluginManager):
    pm.register(EventSourceSqlite())
