
from dataclasses import dataclass

model_type_key = ['model_config', 'model_type']
upstream_model_keys = ['input_hierarchy', 'models']

@dataclass
class ConfigSettings:
    model_type_key: list[str]
    upstream_model_keys: list[str]

    def __post_init__(self):
        self.model_type_key = model_type_key
        self.upstream_model_keys = upstream_model_keys
