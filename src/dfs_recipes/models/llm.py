from datetime import datetime
from typing import Optional, List, Sequence, Dict, Literal, Annotated, TypedDict
from uuid import uuid4
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, UUID4, field_validator, field_serializer, computed_field


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


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
