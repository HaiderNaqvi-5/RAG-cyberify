from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.config import DSN

pool = ConnectionPool(
    DSN,
    min_size=1,
    max_size=8,
    open=True,
    kwargs={"row_factory": dict_row},
)

def query(sql: str, params: tuple = ()) -> list[dict]:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def execute(sql: str, params: tuple = ()) -> dict | None:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description is None:
                return None
            return cur.fetchone()