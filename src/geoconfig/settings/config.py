
# from dataclasses import dataclass

model_type_key = ['model_config', 'model_type']
upstream_model_keys = ['input_hierarchy', 'models']

# cache seetings
input_sources_keys = ['input_sources']
input_cache_keys = ['input_cache']

# model parameters


# schema filepaths
schema_filepaths = [r'src\geoconfig\settings\input_schema.yaml']


# @dataclass
# class ConfigSettings:
#     model_type_key: list[str]
#     upstream_model_keys: list[str]
#     schemas: list[str]

#     def __post_init__(self):
#         self.model_type_key = model_type_key
#         self.upstream_model_keys = upstream_model_keys
#         self.schemas = schema_filepaths
