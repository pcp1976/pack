import sqlite3
from sqlite3.dbapi2 import OperationalError, IntegrityError
import json
from api.eventsource import Event
import uuid
import datetime

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


class TableAdapter:
    def __init__(self, file_path):
        self.con = sqlite3.connect(file_path)

    def delete_subscription(self, subscription_name):
        raise NotImplementedError

    @staticmethod
    def stream_name(stream_name):
        return f"stream_{stream_name}"

    def create_stream_table(self, stream_name):
        cur = self.con.cursor()
        cur.execute(
            "".join(
                [
                    f"CREATE TABLE {self.stream_name(stream_name)} ",
                    "(id TEXT PRIMARY KEY, ",
                    "type TEXT NOT NULL, ",
                    "data TEXT NOT NULL, ",
                    "metadata text NOT NULL, ",
                    "raised_time text NOT NULL",
                    ");",
                ]
            )
        )

    def register_handler(self, stream_name, subscription_name, event_handler):
        f_name = f"{stream_name}_{subscription_name}_{event_handler.__name__}"
        cur = self.con.cursor()
        self.con.create_function(f_name, 5, event_handler)
        try:
            cur.execute("".join([
                f"CREATE TRIGGER {f_name} AFTER INSERT ON stream_{stream_name} ",
                f"BEGIN SELECT {f_name}(NEW.id, NEW.type, NEW.data, NEW.metadata, NEW.raised_time); END;"
            ]))
            self.con.commit()
        except OperationalError as e:
            print(e)

    def create_subscription(self, stream, subscription):
        cur = self.con.cursor()
        try:
            cur.execute(
                f'INSERT INTO subscriptions ("stream", "subscription") VALUES ("{self.stream_name(stream)}", "{subscription}");'
            )
            self.con.commit()
        except IntegrityError as e:
            print(str(e))  # subscription already exists

    def create_subscription_table(self):
        cur = self.con.cursor()
        try:
            cur.execute(
                'CREATE TABLE subscriptions ("stream" TEXT, "subscription" TEXT, PRIMARY KEY("stream","subscription"));'
            )
        except OperationalError as e:
            if str(e).find("already exists") > 0:
                pass
            else:
                raise e

    def append_event(self, stream_name, event: Event):
        cur = self.con.cursor()
        # raised_time set here - when the event is raised onto its destination stream
        # uuid based on streram and time of event to prevent collisions
        raised_time = datetime.datetime.now()
        sql_str = "".join(
            [
                f"INSERT INTO {self.stream_name(stream_name)} (id, type, data, metadata, raised_time) ",
                f"VALUES (",
                f"'{str(uuid.uuid5(uuid.NAMESPACE_URL, f'{stream_name}_{raised_time}'))}', "
                f"'{event.type}', ",
                f"'{json.dumps(event.data)}', ",
                f"'{json.dumps(event.metadata)}', ",
                f"'{raised_time}');",
            ]
        )
        cur.execute(sql_str)
        self.con.commit()
