import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
import aiosqlite
import json
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Checkpointer

log = logging.getLogger(__name__)

CREATE_USER_SESSION_TABLE = """
                            create table if not exists user_session (user_id text not null,
                                                                     session text not null default '{}',
                                                                     primary key (user_id)); \
                            """

SELECT_USER_SESSION_SQL = """
                          select user_id,
                                 session
                          from user_session
                          where user_id = ?; \
                          """

UPDATE_USER_SESSION_SQL = """
                          replace
                          into user_session (user_id, session)
                          values (?, ?); \
                          """


class SQLiteClient:
    def __init__(self, db_name: str):
        self.db_path = Path(__file__).parent / db_name

    async def init(self) -> None:
        try:
            log.info('initializing SQLite database')
            async with self.get_connection() as conn:
                await conn.execute(CREATE_USER_SESSION_TABLE)
                await conn.commit()
                log.info('SQLite database initialized successfully')
        except Exception as e:
            log.error(f'Error initializing SQLite database: {e}', exc_info=True)
            raise

    async def fetch_session(self, user_id: str) -> dict:
        async with self.get_connection() as conn:
            async with conn.execute(SELECT_USER_SESSION_SQL, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[1])
                return {}

    async def update_session(self, user_id: str) -> dict:
        async with self.get_connection() as conn:
            async with conn.execute(UPDATE_USER_SESSION_SQL, (user_id, '{}')) as cursor:
                await conn.commit()
                return {}

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[aiosqlite.Connection]:
        conn = await aiosqlite.connect(self.db_path)
        try:
            yield conn
        finally:
            await conn.close()

    @asynccontextmanager
    async def get_checkpointer(self) -> AsyncIterator[Checkpointer]:
        async with AsyncSqliteSaver.from_conn_string(self.db_path) as checkpointer:
            yield checkpointer

    async def create_tables(self):
        async with self.get_connection() as conn:
            await conn.execute(CREATE_USER_SESSION_TABLE)
            await conn.commit()
