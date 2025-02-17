from abc import ABC
from .InputConfig import InputConfig

type_map = {
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'bool': bool,
    }


class SchemaConfig(InputConfig):

    def __init__(self, filepath=None, filespec=None, type_map=type_map):
        super().__init__(filepath)
       
        self._schema = self.input_dict
        self._type_map = type_map
        self._type_map.update(self._UserInputClassifier.input_factory.list_all())
    
    @property
    def schema(self):
        return self._schema
    
    def validate(self, config: dict):
        # Validate the config against the schema
        return self._validate_schema_level(config, self.schema)
    
    def _validate_schema_level(self, config: dict, schema_level, path_prefix=None):
        # if not isinstance(config, dict):
        #     raise ValueError(f"Expected a dictionary, got {config}")
        
        # for key, rules in schema_level.items():
        #     current_path = f'{path_prefix}.{key}' if path_prefix else key

        #     if 'required' in rules and rules['required']=='true' and key not in config:
        #         raise ValueError(f"Missing required key {current_path}")
            
        #     if key in config:
        #         config_value = config[key]
        #         if 'value_type' in rules:
        #             expected_type = rules['value_type']
        #             pass
        
        #         if 'schema' in rules:
        #             if not isinstance(config_value, dict):
        #                 raise ValueError(f"Expected a dictionary, got {config_value}")
                    
        #             self._validate_schema_level(config_value, rules['schema'], current_path)

        return print('validation successful - haha nope - not implemented yet')

