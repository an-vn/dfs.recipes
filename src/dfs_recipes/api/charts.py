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
    # return {"chart_title":"Points Scored Over Time","chart_type":"Bar Chart","javascript":"\nconst createChartOptions = (data) => {\n    // Sort data by date in ascending order\n    const sortedData = data.sort((a, b) => new Date(a.DATE) - new Date(b.DATE));\n\n    // Extract dates for the x-axis and points for the y-axis\n    const dates = sortedData.map(item => item.DATE);\n    const points = sortedData.map(item => item.PTS);\n\n    return {\n        title: {\n            text: 'Points Scored Over Time',\n            subtext: 'Data for Angel Reese (2024 REG)',\n            left: 'center'\n        },\n        tooltip: {\n            trigger: 'axis',\n            axisPointer: {\n                type: 'shadow'\n            }\n        },\n        grid: {\n            left: '3%',\n            right: '4%',\n            bottom: '10%',\n            containLabel: true\n        },\n        xAxis: {\n            type: 'category',\n            data: dates,\n            axisLabel: {\n                rotate: 45,\n                interval: 0\n            }\n        },\n        yAxis: {\n            type: 'value',\n            name: 'Points Scored'\n        },\n        dataZoom: [\n            {\n                type: 'slider',\n                start: 0,\n                end: 100,\n                bottom: 10\n            },\n            {\n                type: 'inside',\n                start: 0,\n                end: 100\n            }\n        ],\n        series: [{\n            name: 'Points Scored',\n            type: 'bar',\n            data: points,\n            itemStyle: {\n                color: '#c23531'\n            },\n            markPoint: {\n                data: [\n                    { type: 'max', name: 'Max Points' },\n                    { type: 'min', name: 'Min Points' }\n                ]\n            },\n            markLine: {\n                data: [\n                    { type: 'average', name: 'Average Points' }\n                ]\n            }\n        }]\n    };\n};\n","explanation":"This bar chart displays the total points scored in each game over time. The data is sorted chronologically to show performance trends. The x-axis represents the game date, and the y-axis represents the points scored. You can hover over the bars to see the exact points for each game and use the slider at the bottom to zoom in on a specific time period."}


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

