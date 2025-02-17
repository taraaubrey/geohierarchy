from abc import ABC
from .InputConfig import InputConfig


class UserConfig(InputConfig):
    def __init__(self, filepath=None, filespec=None):
        super().__init__(filepath, filespec)
        
        # TODO: make this a parameter
        self.hiera_model_code = 'input_hierarchy.models'

        self._flatspecs = self._classify_yaml_specs(self.input_dict)
        self._specs = self._flat_to_nested(self._flatspecs)
        self._upstream_specs = self._set_upstream_specs()

    @property
    def specs(self):
        return self._specs
    
    @property
    def upstream_specs(self):
        return self._upstream_specs

   
    def _set_upstream_specs(self):
        other_yamls = [(key.split('.')[-1], value) for key, value in self.specs.items() if self.hiera_model_code in key]

        model_specs = []

        for key, model_yamlinput in other_yamls:

            # new spec
            hlevel = int(key.split('.')[-1])
            hspec = HierarchicalInputConfig.from_spec(model_yamlinput)
            hspec.add_hierarchy_level(hlevel)
            model_specs.append(hspec)
            
        return model_specs
    
    def _classify_yaml_specs(self, yaml_config: dict, parent_key_prefix: str = ""):
        yaml_specs = {}
        for key, value in yaml_config.items():
            raw_yaml_key = key if not parent_key_prefix else f"{parent_key_prefix}.{key}"

            # Recursive call for nested structures
            if isinstance(value, dict):
                yaml_update = self._classify_yaml_specs(value, parent_key_prefix=raw_yaml_key)
                yaml_specs.update(yaml_update)
            else:
                yaml_specs[raw_yaml_key] = self.get_spec_type(value)
        return yaml_specs

    def _flat_to_nested(self, flat_dict):
        nested_dict = {}
        for key, value in flat_dict.items():
            keys = key.split('.')
            current_dict = nested_dict
            for k in keys[:-1]:
                current_dict = current_dict.setdefault(k, {})
            current_dict[keys[-1]] = value
        return nested_dict

    def validate(self, schema_config: InputConfig):
        # Validate the config against the schema
        return schema_config.validate(self.specs)
    
    def get_model_type(self):
        return self.specs.get('model_config').get('model_type').value


class HierarchicalInputConfig(UserConfig):
    def __init__(self, filepath=None, filespec=None):
        super().__init__(filepath, filespec)
        self._hlevel = None
    
    @property
    def hlevel(self):
        return self._hlevel
        
    def add_hierarchy_level(self, hierarchy_level):
        # check level is an integer
        if not isinstance(hierarchy_level, int):
            raise ValueError(f"Invalid hierarchy level: {hierarchy_level}. Input is a {type(hierarchy_level)} Must be an integer.")
        
        self._hlevel = hierarchy_level
    
	
