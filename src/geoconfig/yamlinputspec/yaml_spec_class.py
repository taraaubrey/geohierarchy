from typing import Any, List, Optional, Dict
from dataclasses import dataclass

from os.path import basename, isfile
from yaml import load, BaseLoader

from geoconfig.yamlinputspec.spectypeclassifier import get_value_spec_type

class YamlSpec:
    def __init__(self, filespec):
        
        self.hiera_model_code = 'input_hierarchy.models'

        # self.filepath = filepath
        self.filespec = filespec

        input_dict = self.filespec.open()

        self._specs = self._classify_yaml_specs(input_dict)
        self._upstream_specs = self._set_upstream_specs()

    def __repr__(self):
        return f"YamlSpec({self.basename})"

    @property
    def specs(self):
        return self._specs
    
    @property
    def upstream_specs(self):
        return self._upstream_specs

    @classmethod
    def from_filepath(cls, filepath):
        filespec = get_value_spec_type(filepath)
        return cls.from_spec(filespec)

    @classmethod
    def from_spec(cls, filespec):
        return cls(filespec)
    
    def _set_upstream_specs(self):
        other_yamls = [(key.split('.')[-1], value) for key, value in self.specs.items() if self.hiera_model_code in key]

        model_specs = []

        for key, model_yamlinput in other_yamls:

            # new spec
            hlevel = int(key.split('.')[-1])
            hspec = HierarchicalYamlSpec.from_spec(model_yamlinput)
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
                yaml_specs[raw_yaml_key] = get_value_spec_type(value)
        return yaml_specs


class HierarchicalYamlSpec(YamlSpec):
    def __init__(self, filepath):
        super().__init__(filepath)
        self._hlevel = None
    
    @property
    def hlevel(self):
        return self._hlevel
        
    def add_hierarchy_level(self, hierarchy_level):
        # check level is an integer
        if not isinstance(hierarchy_level, int):
            raise ValueError(f"Invalid hierarchy level: {hierarchy_level}. Input is a {type(hierarchy_level)} Must be an integer.")
        
        self._hlevel = hierarchy_level
    
	
