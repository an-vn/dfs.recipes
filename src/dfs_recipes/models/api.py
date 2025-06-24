from pydantic import BaseModel, Field, field_validator, computed_field
from dfs_recipes.utils import data_utils
from dfs_recipes.config.settings import settings


class MessageRequest(BaseModel):
    message: str = Field(
        description='User message to be processed by the model',
        pattern=r'^[A-Za-z0-9\s!?.\'",:-]+$',
        max_length=settings.user_input_character_limit,
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

