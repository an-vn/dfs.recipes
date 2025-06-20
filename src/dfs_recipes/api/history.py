import logging
import json
import uuid
from typing import Annotated
from pathlib import Path
from collections.abc import AsyncIterable
from fastapi import APIRouter, Request, Response, BackgroundTasks, Cookie
from fastapi.responses import StreamingResponse
from dfs_recipes.database.checkpoints import db_client
from dfs_recipes.models import MessageRequest
from dfs_recipes.agents import echarts_agent
from dfs_recipes.utils import data_utils

log = logging.getLogger(__name__)

router = APIRouter()


# @router.get('/history')
async def get_history(request: Request):
    try:
        async with db_client.get_checkpointer() as checkpointer:
            config = data_utils.build_graph_config(request.session['thread_id'])
            graph = echarts_agent.workflow.compile(checkpointer=checkpointer)
            state = await graph.aget_state(config)
            log.info(state.values)
            messages = [
                # {
                #     'type': msg.type,
                #     'content': msg.content,
                # }
                # for msg in state.values['messages']
                # if msg.type in {'human', 'ai'} and msg.content
            ]

        return messages
    except Exception as e:
        log.error(f'Error fetching history: {e}', exc_info=True)
        return []


# @router.delete('/history')
async def delete_history(request: Request):
    return []
