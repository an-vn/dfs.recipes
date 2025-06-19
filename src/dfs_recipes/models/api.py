from datetime import datetime
from typing import Optional, List, Sequence, Dict, Literal, Annotated, TypedDict
from urllib.parse import quote_plus, unquote_plus
from uuid import uuid4
from cryptography.fernet import Fernet
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, UUID4, field_validator, field_serializer, computed_field
from dfs_recipes.utils import data_utils


class MessageRequest(BaseModel):
    message: str = Field(
        description='User message to be processed by the model',
        pattern=r'^[A-Za-z0-9\s!?.\'",:-]+$',
        max_length=500,
    )

    @field_validator('message', mode='after')
    @classmethod
    def sanitize(cls, msg: str) -> str:
        return ' '.join(msg.split())


class ChartRequest(MessageRequest):
    dataset: list[dict] = Field(
        description='The dataset to be used for the chart.',
    )

    @computed_field
    @property
    def dataset_description(self) -> str:
        return 'Array of objects containing basketball game data'

    @computed_field
    @property
    def dataset_sample(self) -> str:
        return data_utils.sample_dataset(self.dataset)

