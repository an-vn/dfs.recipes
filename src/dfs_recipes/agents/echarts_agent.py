import os
import logging
import json
import uuid
from collections.abc import AsyncIterable
from datetime import datetime
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from dfs_recipes.database.checkpoints import db_client
from dfs_recipes.models import AgentState, ChartRequest, ChartResponse
from dfs_recipes.utils import data_utils

log = logging.getLogger(__name__)

model = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro-preview-06-05')

prompt_template = """\
You are an Apache Echarts expert.

Write a JavaScript function `createChartOptions` that generates an Apache ECharts configuration object based on the provided data and user's data visualization requirements.
Perform any necessary data transformations to prepare the data for visualization.

[BEGIN DATA]
************

OUTPUT FORMAT:
const createChartOptions = (data) => {{
    // YOUR CODE GOES HERE - perform any necessary data transformations here
    
    return {{
        // YOUR CODE GOES HERE - return an ECharts configuration object
    }}
}};

USER REQUIREMENTS:
{user_requirements}

DATASET DESCRIPTION:
{dataset_description}

DATASET SAMPLE:
{dataset_sample}

************
[END DATA]
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=[
        'user_requirements',
        'dataset_description',
        'dataset_sample',
    ]
)

llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0,
    max_retries=2,
    google_api_key=os.environ['GEMINI_API_KEY'],
)

chain = prompt | llm.with_structured_output(schema=ChartResponse)

async def invoke_chain(chart: ChartRequest, thread_id: str) -> ChartResponse:
    """ Invoke the chain with the provided message and thread ID. """
    graph_config = data_utils.build_graph_config(thread_id)
    response = await chain.ainvoke(
        input={
            'user_requirements': chart.message,
            'dataset_description': chart.dataset_description,
            'dataset_sample': chart.dataset_sample,
        },
        config=graph_config,
    )
    return response


workflow = StateGraph(AgentState)

def generate(state: AgentState):
    ...

async def stream_graph(message: ChartRequest, thread_id: str) -> AsyncIterable[str]:
    async with db_client.get_checkpointer() as checkpointer:
        graph_config = data_utils.build_graph_config(thread_id)
        graph = workflow.compile(checkpointer=checkpointer)
        async for msg, metadata in graph.astream(
                input={'messages': [('user', message)]},
                config=graph_config,
                stream_mode='messages',
        ):
            if msg.content:
                yield msg.content

