from pluggy import HookimplMarker, PluginManager
from configobj import ConfigObj

from api.eventsource import Event, EventSource
from api.plugin import Plugin

eventsource = HookimplMarker("pack")


class EventSourceMemory(EventSource, Plugin):
    """
    Simple, volatile event source using dicts
    """

    def __init__(self):
        super().__init__()
        self.name = "eventsource_memory"
        self.streams = {}
        self.subscriptions = {}

    @eventsource
    def plugin_pm_link(self, pm: PluginManager):
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

    def command_handler(self, event):
        raise NotImplementedError(event)

    def apply_config(self, config):
        self.config_obj = config

    @eventsource
    def config_inject(self, config):
        fresh_config = self._config_mung(config)
        if not fresh_config["EVENTSOURCE_TYPE"] == self.name:
            print(f"{self.name} unwanted; die")
            self.pm.unregister(self)
        else:
            self.apply_config(fresh_config)

    @eventsource
    def register_event_handler(self, stream_name, subscription_name, event_handler):
        """
        :param stream_name: name of the stream the event_handler receives events from
        :param subscription_name: identifier for the subscription
        :param event_handler: function which will receive events from the stream
        :return: None
        """
        if event_handler not in self.subscriptions[stream_name][subscription_name]:
            self.subscriptions[stream_name][subscription_name].append(event_handler)
        for event in self.streams[stream_name]:
            event_handler(event)

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
            self.subscriptions[stream_name].remove(subscription_name)

    @eventsource
    def create_subscription(self, stream_name, subscription_name):

        if stream_name not in self.streams:
            self.streams.update({stream_name: []})
        if stream_name not in self.subscriptions:
            self.subscriptions.update({stream_name: {}})
        if subscription_name not in self.subscriptions[stream_name]:
            self.subscriptions[stream_name].update({subscription_name: []})

    @eventsource
    def raise_event(self, stream_name: str, event: Event):
        if stream_name not in self.streams:
            self.streams[stream_name] = []
        self.streams[stream_name].append(event)
        try:
            for sub in self.subscriptions[stream_name]:
                for callback in self.subscriptions[stream_name][sub]:
                    callback(event)
        except KeyError:
            pass

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
    pm.register(EventSourceMemory())
