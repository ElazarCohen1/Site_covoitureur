import psycopg2 as pg
from psycopg2.extras import NamedTupleCursor

def connect():
    conn = pg.connect(
        user="elazar",
        dbname="projet",
        cursor_factory=NamedTupleCursor
    )
    conn.autocommit = True
    return conn

