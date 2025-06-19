import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from langgraph.types import Checkpointer
from langgraph.checkpoint.memory import InMemorySaver


class InMemoryClient:
    async def init(self) -> None:
        ...

    @asynccontextmanager
    async def get_checkpointer(self) -> AsyncIterator[Checkpointer]:
        async with InMemorySaver() as checkpointer:
            yield checkpointer
