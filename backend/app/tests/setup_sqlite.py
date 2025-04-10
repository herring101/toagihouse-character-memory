import json
import sqlite3
from sqlite3 import Connection as SQLite3Connection

from sqlalchemy import event
from sqlalchemy.engine import Engine


# SQLiteでJSON型をサポートするための設定
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# JSONをシリアライズ・デシリアライズするためのアダプター
def adapt_json(val):
    return json.dumps(val)


def convert_json(val):
    return json.loads(val)


# SQLiteにJSONを登録
sqlite3.register_adapter(dict, adapt_json)
sqlite3.register_converter("json", convert_json)
