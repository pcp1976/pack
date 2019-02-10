from pluggy import PluginManager
from configobj import ConfigObj
import datetime


class Event:
    def __init__(self, **kwargs):
        self.data: dict = None
        self.id: str = None
        self.metadata: dict = None
        self.type: str = None
        self._raised_time = str(datetime.datetime.now())
        for k, v in kwargs:
            self.__dict__.update({k, v})

    @property
    def raised_time(self):
        return self._raised_time

    @raised_time.setter
    def raised_time(self, value):
        pass


class EventSource:
    """
    Interface for eventsources
    """

    def __init__(self):
        self.name = None
        self.pm: PluginManager = None
        self.config_obj: ConfigObj = None

    def register_event_handler(self, stream_name, subscription_name, event_handler):
        """
        :param stream_name: name of the stream the event_handler receives events from
        :param subscription_name: identifier for the subscription
        :param event_handler: function which will receive events from the stream
        :return: None
        """
        raise NotImplementedError

    def deregister_event_handler(self, event_handler):
        """
        :param event_handler: function which will no longer receive events from the stream
        :return: None
        """
        raise NotImplementedError

    def delete_subscription(self, stream_name, subscription_name):
        """
        :param stream_name: name of the stream to delete the subscription from
        :param subscription_name: identifier of the subscription to delete
        :return: None
        """
        raise NotImplementedError

    def create_subscription(self, stream_name, subscription_name):
        """
        create a named subscription to a stream
        :param stream_name: name of the stream to subscribe to
        :param subscription_name: name of the subscription
        """
        raise NotImplementedError

    def raise_event(self, stream_name: str, event: Event):
        raise NotImplementedError

    def start_event_streams(self) -> bool:
        """
        Start up the event streams
        :return: bool True on success
        """
        raise NotImplementedError

    def stop_event_streams(self) -> bool:
        """
        Stop event streams
        :return: bool True on success
        """
        raise NotImplementedError
