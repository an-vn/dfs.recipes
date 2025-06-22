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

# scatter-exponential-regression

@router.post('/chart')
async def generate_chart(request: Request, chart: ChartRequest, background_tasks: BackgroundTasks):
    data = await echarts_agent.invoke_chain(chart, request.session['thread_id'])
    return data
    # return {"chart_title":"Player Performance: Points, Rebounds, and Assists Over Time","chart_type":"stacked_bar","javascript":"\nconst createChartOptions = (data) => {\n    // Sort data by date in ascending order\n    const sortedData = data.sort((a, b) => new Date(a.DATE) - new Date(b.DATE));\n\n    // Extract the data for the chart\n    const dates = sortedData.map(item => item.DATE);\n    const points = sortedData.map(item => item.PTS);\n    const rebounds = sortedData.map(item => item.REB);\n    const assists = sortedData.map(item => item.AST);\n\n    return {\n        title: {\n            text: \"Player Performance Over Time\",\n            subtext: \"Points, Rebounds, and Assists\",\n            left: \"center\"\n        },\n        tooltip: {\n            trigger: \"axis\",\n            axisPointer: {\n                type: \"shadow\"\n            }\n        },\n        legend: {\n            data: [\"Points\", \"Rebounds\", \"Assists\"],\n            top: \"bottom\"\n        },\n        grid: {\n            left: \"3%\",\n            right: \"4%\",\n            bottom: \"10%\",\n            containLabel: true\n        },\n        xAxis: {\n            type: \"category\",\n            data: dates,\n            name: \"Date\",\n            nameLocation: \"middle\",\n            nameGap: 30\n        },\n        yAxis: {\n            type: \"value\",\n            name: \"Count\"\n        },\n        series: [\n            {\n                name: \"Points\",\n                type: \"bar\",\n                stack: \"total\",\n                emphasis: {\n                    focus: \"series\"\n                },\n                data: points\n            },\n            {\n                name: \"Rebounds\",\n                type: \"bar\",\n                stack: \"total\",\n                emphasis: {\n                    focus: \"series\"\n                },\n                data: rebounds\n            },\n            {\n                name: \"Assists\",\n                type: \"bar\",\n                stack: \"total\",\n                emphasis: {\n                    focus: \"series\"\n                },\n                data: assists\n            }\n        ]\n    };\n};\n","explanation":"This stacked bar chart visualizes Angel Reese's performance over time, specifically showing the breakdown of points, rebounds, and assists for each game. The bars are stacked to represent the total of these three statistics (PRA) for a given date. The x-axis represents the game date, and the y-axis represents the total count. This allows for a clear comparison of performance across different games.","user_requirements":"stacked bar chart showing points rebounds assists over time"}


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

