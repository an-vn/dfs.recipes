import logging
import random
from datetime import datetime, timezone

import pandas as pd
from langchain_core.runnables.config import RunnableConfig

log = logging.getLogger(__name__)


def datetime_to_iso_8601(dt: datetime) -> str:
    """Convert a datetime object to ISO 8601 format."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def datetime_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def build_graph_config(thread_id: str) -> RunnableConfig:
    return {
        'configurable': {
            'thread_id': thread_id,
        }
    }


def sample_dataset(data: list[dict], sample_size: int = 10) -> str:
    prompt = ''
    prompt += '[\n'
    samples = random.sample(data, min(len(data), sample_size))
    for obj in samples:
        prompt += f'\t{obj}\n'
    prompt += ']'
    return prompt


def build_dataset_metadata(df: pd.DataFrame) -> dict:
    json_keys = df.columns.tolist()
    item_count = len(df)

    metadata = {
        'item_count': item_count,
        'attributes': {},
    }

    for col in json_keys:
        series = df[col]
        metadata['attributes'][col] = {}
        num_unique = series.nunique()
        d = series.describe().to_dict()

        if 'mean' in d:
            metadata['attributes'][col] |= {
                'Data Type': 'number',
                'Unique Items': num_unique,
                'Mean': round(d['mean'], 2),
                'Standard Deviation': round(d['std'], 2),
                'Min Value': round(d['min'], 2),
                'Max Value': round(d['max'], 2),
            }
        else:
            metadata['attributes'][col] |= {
                'Data Type': 'string',
                'Unique Items': num_unique,
                'Top Occurrence': f'{d['top']} ({d['freq']})'
            }
    return metadata
