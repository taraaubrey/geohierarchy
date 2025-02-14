from typing import Dict, Any
from os.path import isfile

from geoconfig.yamlinputspec.input_types.definitions import (
    ValueInput,
    FilenameInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
)

class SpecTypeClassifier:
    def __init__(self):
        # get registered spec types
        self.spec_types = {
            "filename": "filename",
            "cached": "cached",
            "python_module": "python_module",
            "multi": "multi",
            "value": "value",
        }
    
    def get_spec_type(self, raw_yaml_key, key, value):
        spec_type, parsed_value = self._determine_spec_type(key, value)
        return self._assign_spec_type(raw_yaml_key, parsed_value, spec_type)
   
    def _determine_spec_type(self, key, value) -> str:
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
            spec_list, value_list = self._determine_list_spec_type(key, values)
            return spec_list, self._determine_python_module(char, value_list)
        elif isinstance(value, str) and value.split(":")[0] == "$":
            return "cached", value
        elif isinstance(value, str) and value.split(":")[0] == "$py":
            values = value.split("(")[1].split(")")[0].replace(" ", "").split(",")
            spec_list, value_list = self._determine_list_spec_type(key, values)
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
            spec_list, value_list = self._determine_list_spec_type(key, value)
            return spec_list, {"type": "multi", "values": value_list}
        elif isinstance(value, (float, int, str, bool)):
            return "value", value
        else:
            raise ValueError(f"Unknown spec type for key: {key}, value: {value}")

    def _determine_python_module(self, char, values):
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

    def _determine_list_spec_type(self, key, value):
        value_list = []
        spec_list = []
        for item in value:
            spec_type, value = self._determine_spec_type(key, item)
            spec_list.append(spec_type)
            value_list.append(value)
        return spec_list, value_list

    def _assign_list_spec_type(self, raw_yaml_key, value_list, spec_list: str):
        # enumerate value list
        input_type = []
        for i, item in enumerate(value_list):
            input_type.append(self._assign_spec_type(raw_yaml_key, item, spec_list[i]))
        return input_type

    def _assign_spec_type(self, raw_yaml_key, value, spec_type: str) -> str:
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
                value_list = self._assign_list_spec_type(raw_yaml_key, value, spec_type)
                return MultiInput(
                    type="multi", values=value_list, raw_yaml_key=raw_yaml_key
                )
            elif value["type"] == "python_module":
                args_list = self._assign_list_spec_type(raw_yaml_key, value["values"], spec_type)
                return PythonModuleInput(
                    type="python_module",
                    module=value["module"],
                    function=value["function"],
                    args=args_list,
                    raw_yaml_key=raw_yaml_key,
                )
        else:
            raise ValueError(f"Unknown spec type for key: {raw_yaml_key}, value: {value}")

def get_value_spec_type(raw_yaml_key, key, value):
    classifier = SpecTypeClassifier()
    return classifier.get_spec_type(raw_yaml_key, key, value)