from typing import Any, List, Optional, Dict
from dataclasses import dataclass

from os.path import basename, isfile
from yaml import load, BaseLoader

from geoconfig.yamlinputspec.YamlInputSpec_base import (
    YamlInputSpec,
    ValueInput,
    FilenameInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
)


class YamlSpec:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = self._get_basename()
        self._specs = self._map_config()
        self._upstream_specs = self._set_upstream_specs()

    @property
    def specs(self):
        return self._specs
    
    @property
    def upstream_specs(self):
        return self._upstream_specs

    @classmethod
    def from_filename(cls, filename):
        return cls(filename)

    def _parse_yaml_file(self) -> dict:
        """1. Opens the yaml file and loads it into a python dictionary."""
        with open(self.filepath, "r") as file:
            yaml_config = load(file, Loader=BaseLoader)
        return yaml_config

    def _get_basename(self):
        return basename(self.filepath).split(".")[0]

    def _map_config(self):
        yaml_config = self._parse_yaml_file()
        return _classify_yaml_specs(yaml_config)
    
    def _set_upstream_specs(self):
        other_yamls = [(key.split('.')[-1], value) for key, value in self.specs.items() if "input_hierarchy.models" in key]

        model_specs = []
        for key, model_yamlinput in other_yamls:
            # open file
            if isinstance(model_yamlinput, FilenameInput):
                model_yaml_filepath = model_yamlinput.filename
            else:
                raise ValueError(f"Model yaml file path not found for {key}")
            
            # new spec
            hlevel = int(key.split('.')[-1])
            hspec = HierarchicalYamlSpec.from_filename(model_yaml_filepath)
            hspec.add_hierarchy_level(hlevel)
            model_specs.append(hspec)
            
        return model_specs


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
	

    


def determine_spec_type(key: str, value: Any) -> str:
    """Type determination of input specs based on key and value."""
    # Value type can be float, int, str, bool
    if isinstance(value, str) and isfile(
        value
    ):  # basic filename check #TODO better filename check
        return "filename", value
    # check if any math symbols are in the string
    elif isinstance(value, str) and any(
        [char in value for char in ["+", "-", "*", "/"]]) and value.startswith("("):
        # find the math symbols and split the string
        for char in ["+", "-", "*", "/"]:
            if char in value:
                values = value.replace(" ", "").replace("(", "").replace(")", "").split(char)
                break
        spec_list, value_list = determine_list_spec_type(key, values)
        return spec_list, determine_python_module(char, value_list)
    elif isinstance(value, str) and value.split(":")[0] == "$":
        return "cached", value
    elif isinstance(value, str) and value.split(":")[0] == "$py":
        values = value.split("(")[1].split(")")[0].replace(" ", "").split(",")
        spec_list, value_list = determine_list_spec_type(key, values)
        module = value.split(":")[1].split("(")[0].split(".")[:-1]
        function = value.split(":")[1].split("(")[0].split(".")[-1]
        return spec_list, {
            "type": "python_module",
            "module": module,
            "function": function,
            "values": value_list,
        }
    elif isinstance(value, list):
        # create recursive for each item in the list
        spec_list, value_list = determine_list_spec_type(key, value)
        return spec_list, {"type": "multi", "values": value_list}
    elif isinstance(value, (float, int, str, bool)):
        return "value", value
    else:
        raise ValueError(f"Unknown spec type for key: {key}, value: {value}")

def determine_python_module(char, values):
    if char == "+":
        return {
            "type": "python_module",
            "module": ["numpy"],
            "function": "add",
            "values": values,
        }
    elif char == "-":
        return {
            "type": "python_module",
            "module": ["numpy"],
            "function": "subtract",
            "values": values,
        }
    elif char == "*":
        return {
            "type": "python_module",
            "module": ["numpy"],
            "function": "multiply",
            "values": values,
        }
    elif char == "/":
        return {
            "type": "python_module",
            "module": ["numpy"],
            "function": "divide",
            "values": values,
        }

def determine_list_spec_type(key, value):
    value_list = []
    spec_list = []
    for item in value:
        spec_type, value = determine_spec_type(key, item)
        spec_list.append(spec_type)
        value_list.append(value)
    return spec_list, value_list

def assign_list_spec_type(raw_yaml_key, value_list, spec_list: str):
    # enumerate value list
    input_type = []
    for i, item in enumerate(value_list):
        input_type.append(assign_spec_type(raw_yaml_key, item, spec_list[i]))
    return input_type

def assign_spec_type(raw_yaml_key, value, spec_type: str) -> str:
    if spec_type == "value":
        return ValueInput(type="value", value=value, raw_yaml_key=raw_yaml_key)
    elif spec_type == "filename":
        return FilenameInput(type="filename", filename=value, raw_yaml_key=raw_yaml_key)
    elif spec_type == "cached":
        value = value.split(":")[-1]  # Remove $: from source
        return CachedInput(type="cached", source=value, raw_yaml_key=raw_yaml_key)
    elif isinstance(value, dict):
        if value["type"] == "multi":
            # return a MultiInputSpec with the list of values
            value_list = assign_list_spec_type(raw_yaml_key, value, spec_type)
            return MultiInput(
                type="multi", values=value_list, raw_yaml_key=raw_yaml_key
            )
        elif value["type"] == "python_module":
            args_list = assign_list_spec_type(raw_yaml_key, value["values"], spec_type)
            return PythonModuleInput(
                type="python_module",
                module=value["module"],
                function=value["function"],
                args=args_list,
                raw_yaml_key=raw_yaml_key,
            )
    else:
        raise ValueError(f"Unknown spec type for key: {raw_yaml_key}, value: {value}")

def _classify_yaml_specs(
    yaml_config: dict,
    parent_key_prefix: str = "",
) -> Dict[str, YamlInputSpec]:
    """
    2. Classifies each key-value pair in the yaml config into YamlInputSpec subclasses, handling nested structures recursively.

    Args:
        yaml_config:
            dict: yaml configuration loaded from a yaml file
        parent_key_prefix:
            str: prefix for nested keys
        input_sources:
            str: key for input definitions in the yaml config
    """
    yaml_specs = {}
    for key, value in yaml_config.items():
        raw_yaml_key = key if not parent_key_prefix else f"{parent_key_prefix}.{key}"

        # Recursive call for nested structures
        if isinstance(value, dict):
            yaml_update = _classify_yaml_specs(value, parent_key_prefix=raw_yaml_key)
            yaml_specs.update(yaml_update)
        else:
            spec_type, parsed_value = determine_spec_type(key, value)
            yaml_specs[raw_yaml_key] = assign_spec_type(raw_yaml_key, parsed_value, spec_type)
    return yaml_specs