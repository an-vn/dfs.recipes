import json
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pathlib import Path
from pprint import pprint

combined = []

labels = [
    'team_name',
    'opponent_name',
    'team_formation',
    'result',
    'player',
    'game_position',
    'position',
]

tensor_columns = [
    'accurate_passes_attempt',
    'accurate_passes_total',
    'team_passes',
    'minutes',
    'team_ball_possession',
    'team_passes',
    'team_own_half_passes',
    'team_opposition_half_passes'
]

def create_labels_from_dataset(dataframe: pd.DataFrame, columns: list[str]) -> dict:
    labels_map = {}
    for label in columns:
        unique = sorted(list(dataframe[label].unique()))
        labels_map.setdefault(label, {})
        for i, value in enumerate(unique):
            if isinstance(value, np.int64):
                value = value.item()
            labels_map[label][i] = value
    return labels_map

df = pd.read_csv(Path('premier_league_matchlogs.csv'))
labels_map = json.loads(Path('dataset_labels.json').read_text(encoding='utf-8'))
