from pluggy import HookspecMarker, PluginManager


hs_eventsource = HookspecMarker("pack")


class EventSourceMemory:
    @hs_eventsource
    def eventsource_handler_register(
        self, stream_name, subscription_name, event_handler
    ):
        """
        :param stream_name: name of the stream the event_handler receives events from
        :param subscription_name: identifier for the subscription
        :param event_handler: function which will receive events from the stream
        :return: None
        """
        pass

    @hs_eventsource
    def eventsource_handler_deregister(self, event_handler):
        """
        :param event_handler: function which will no longer receive events from the stream
        :return: None
        """
        pass

    @hs_eventsource
    def eventsource_subscription_delete(self, stream_name, subscription_name):
        """
        :param stream_name: name of the stream to delete the subscription from
        :param subscription_name: identifier of the subscription to delete
        :return: None
        """
        pass

    @hs_eventsource
    def eventsource_subscription_create(self, stream_name, subscription_name):
        pass

    @hs_eventsource
    def eventsource_event_raise(
        self, stream_name: str, event_type: str, event_data: dict, event_metadata: dict
    ):
        pass

    @hs_eventsource
    def eventsource_streams_start(self) -> bool:
        """
        Start up the event streams
        :return: bool True on success
        """
        pass

    @hs_eventsource
    def stop_event_streams(self) -> bool:
        """
        Stop event streams
        :return: bool True on success
        """
        pass


def pack_register(pm: PluginManager):
    pm.add_hookspecs(EventSourceMemory())
