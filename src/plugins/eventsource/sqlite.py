from pluggy import HookimplMarker, PluginManager
from configobj import ConfigObj
import sqlite3

eventsource = HookimplMarker("pack")


def hello(event_type, event_data, event_metada):
    print(f"Hello {event_type}, {event_data}, {event_metada}")


# TODO
"""
Triggers are persistent - need to choose behaviour on startup
- probably should remove as potentially using different composition of app on restart
Need to choose how to map tables and callbacks to streams, subscriptions, and event handlers

drop trigger https://www.sqlite.org/lang_droptrigger.html
select triggers https://stackoverflow.com/questions/18655057/how-can-i-list-all-the-triggers-of-a-database-in-sqlite

looks as if triggers are stored in a central location, so the name will need to be a combination of
the stream name, the subscription name, and possibly the function name to avoid collisions
"""
# # con = sqlite3.connect(":memory:") can use memory
# con = sqlite3.connect("test.db")
# con.create_function("hello", 3, hello)  # function alias, number of args, function
# cur = con.cursor()
# # only if no db
# cur.execute(
#     "".join(
#         [
#             "CREATE TABLE t ",
#             "(event_id INTEGER PRIMARY KEY AUTOINCREMENT, ",
#             "event_type TEXT NOT NULL, ",
#             "event_data TEXT NOT NULL, ",
#             "event_metadata text NOT NULL);",
#         ]
#     )
# )
# # only if !exists(TRIGGER)
# cur.execute(
#     "CREATE TRIGGER xx AFTER INSERT ON t BEGIN SELECT hello(NEW.event_type, NEW.event_data, NEW.event_metadata); END;"
# )
# # can add multiple triggers on table
# cur.execute(
#     "CREATE TRIGGER yy AFTER INSERT ON t BEGIN SELECT hello(NEW.event_type, NEW.event_data, NEW.event_metadata); END;"
# )
# cur.execute(
#     "INSERT INTO t (event_type, event_data, event_metadata) VALUES('{abc}', '{123}', '{£$%}')"
# )


class EventSourceSqlite:
    """
    Fairly simple persistent event source using sqlite3
    """

    name = "eventsource_sqlite"

    def __init__(self):
        self.streams = {}
        self.subscriptions = {}
        self.config_obj: ConfigObj = None
        self.pm: PluginManager = None

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

    def apply_config(self, config):
        self.config_obj = config
        # TODO apply any relevant settings

    @eventsource
    def config_inject(self, config):
        fresh_config = self._config_mung(config)
        if not fresh_config["eventsource"]["type"] == self.name:
            print(f"{self.name} unwanted; die")
            # TODO object should be shunted out of scope and be GC'd
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
    def raise_event(
        self, stream_name: str, event_type: str, event_data: dict, event_metadata: dict
    ):
        if stream_name not in self.streams:
            self.streams[stream_name] = []
        event = {
            "event_type": event_type,
            "event_data": event_data,
            "event_metadata": event_metadata,
        }
        self.streams[stream_name].append(event)
        try:
            for sub in self.subscriptions[stream_name]:
                for callback in self.subscriptions[stream_name][sub]:
                    callback(
                        event_type=event_type,
                        event_data=event_data,
                        event_metadata=event_metadata,
                    )
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
    pm.register(EventSourceSqlite())
