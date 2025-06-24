from typing import Sequence, Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class ChartResponse(BaseModel):
    """ Always use this tool to structure your response to the user. """
    chart_title: str = Field(
        description='The title of the chart',
    )
    chart_type: str = Field(
        description='The type of chart.',
    )
    javascript: str = Field(
        description='JavaScript code to render the chart.',
    )
    explanation: str = Field(
        description='Explanation of the chart.',
    )
    user_requirements: str = Field(
        description='User requirements for the chart.',
    )


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
