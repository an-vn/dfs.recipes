import logging
import json
import uuid
from pathlib import Path
from collections.abc import AsyncIterable
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from dfs_recipes.models import ChartRequest
from dfs_recipes.agents import echarts_agent
from pydantic import ValidationError

log = logging.getLogger(__name__)

router = APIRouter()

_web_dir = Path(__file__).parent.parent / 'web'


async def chart_generation(thread_id: str) -> AsyncIterable[str]:
    msg = json.dumps({
        'thread_id': thread_id,
    })
    yield f'event: callback\ndata: {msg}\n\n'


@router.post('/chart')
async def generate_chart(request: Request, chart: ChartRequest, background_tasks: BackgroundTasks):
    data = await echarts_agent.invoke_chain(chart, request.session['thread_id'])
    return data


# @router.get('/callback/{thread_id}')
async def generation_callback(thread_id: str):
    """ TODO: Callback endpoint for checking generation incase user refreshes the page. """
    return StreamingResponse(chart_generation(thread_id), media_type='text/event-stream')

# @router.post('/message')
async def message(request: Request, msg: ChartRequest):
    """ TODO: Add when ready """
    try:
        return StreamingResponse(
            echarts_agent.stream_graph(msg, request.session['thread_id']),
            media_type='text/event-stream'
        )
    except ValidationError as e:
        error = e.errors()[0]
        match error['type']:
            case 'string_too_long':
                raise HTTPException(
                    status_code=413,
                    detail=f'Message too long: {error["msg"]}'
                )
            case 'string_pattern_mismatch':
                raise HTTPException(
                    status_code=400,
                    detail=f'Message contains invalid characters: {error["msg"]}'
                )
            case _:
                raise HTTPException(
                    status_code=400,
                    detail=error['msg']
                )
    except Exception as e:
        log.error(f'Error processing message: {e}', exc_info=True)
        raise HTTPException(
            status_code=500,
            detail='Internal server error'
        )


# @router.get('/chart')
async def get_chart():
    """ TODO: Add when ready """
    ...


# @router.delete('/chart')
async def delete_chart():
    """ TODO: Add when ready """
    ...

