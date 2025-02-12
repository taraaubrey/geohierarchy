import yaml
from os.path import isfile
from typing import Any, Dict
from .YamlInputSpec_base import (
    YamlInputSpec,
    ValueInput,
    FilenameInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
    DictInput,
)


# --- Parsing Functions ---
def parse_yaml_file(yaml_filepath: str) -> dict:
    """1. Opens the yaml file and loads it into a python dictionary."""
    with open(yaml_filepath, "r") as file:
        yaml_config = yaml.safe_load(file)
    return yaml_config


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
    elif isinstance(value, dict):
        return "dict", value
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
        elif value["type"] == "dict":
            return DictInput(
                type="dict", values=value, raw_yaml_key=raw_yaml_key
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


def classify_yaml_specs(
    yaml_config: dict,
    parent_key_prefix: str = "",
    input_sources="input_sources",
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
            yaml_update = classify_yaml_specs(value, parent_key_prefix=raw_yaml_key)
            yaml_specs.update(yaml_update)
        else:
            spec_type, parsed_value = determine_spec_type(key, value)
            yaml_specs[raw_yaml_key] = assign_spec_type(raw_yaml_key, parsed_value, spec_type)
    return yaml_specs


def check_cached_specs(yaml_specs: Dict[str, YamlInputSpec]) -> None:
    """
    3. Checks that CachedSpec 'source' is defined as a ValueSpec or FilenameSpec.
       Now correctly handles nested raw_yaml_keys for lookup.
    """
    defined_value_filename_keys = {
        spec.raw_yaml_key: spec
        for spec in yaml_specs.values()
        if isinstance(spec, (ValueInput, FilenameInput))
    }

    for spec in yaml_specs.values():
        if isinstance(spec, CachedInput):
            source_key = spec.source  # Source is now the raw_yaml_key of the source
            if source_key not in defined_value_filename_keys:
                raise ValueError(
                    f"CachedSpec '{spec.raw_yaml_key}' source '{spec.source}' "
                    f"not defined as ValueSpec or FilenameSpec."
                )


def resolve_cached_specs(
    yaml_specs: Dict[str, YamlInputSpec],
) -> Dict[str, YamlInputSpec]:
    """
    4. Resolve CachedSpec: Assign CachedSpec as ValueSpec or FilenameSpec based on source.
       5. TransformationSpec handling is also in here in step 6.
       Now correctly resolves sources based on raw_yaml_keys and handles nested structures.
    """
    resolved_specs = {}
    for key, spec in yaml_specs.items():
        if isinstance(spec, CachedInput):
            source_key = spec.source  # Source is the raw_yaml_key
            source_spec = yaml_specs.get(source_key)
            if source_spec:
                if isinstance(source_spec, ValueInput):
                    resolved_specs[key] = ValueInput(
                        type="value",
                        value=source_spec.value,
                        raw_yaml_key=spec.raw_yaml_key,
                    )  # Create ValueInput
                elif isinstance(source_spec, FilenameInput):
                    resolved_specs[key] = FilenameInput(
                        type="filename",
                        filename=source_spec.filename,
                        file_type=source_spec.file_type,
                        raw_yaml_key=spec.raw_yaml_key,
                    )  # Create FilenameInput
                else:  # Should not happen if check_cached_specs is run before
                    raise TypeError(
                        f"CachedSpec '{spec.raw_yaml_key}' source '{spec.source}' is not ValueSpec or FilenameSpec after checking."
                    )
            else:  # Should not happen if check_cached_specs is run before
                raise KeyError(
                    f"CachedSpec source '{spec.source}' for '{spec.raw_yaml_key}' not found in yaml_specs after checking."
                )

        elif isinstance(spec, TransformationInput):
            source_key = spec.source
            source_spec = yaml_specs.get(source_key)

            if source_spec:  # if source spec exists
                if isinstance(source_spec, ValueInput):
                    resolved_specs[key] = ValueInput(
                        type="value",
                        value=source_spec.value,
                        raw_yaml_key=spec.raw_yaml_key,
                    )  # Start with ValueInput
                    resolved_specs[
                        key
                    ].transformation = spec.transform  # Add transformation attribute
                elif isinstance(source_spec, FilenameInput):
                    resolved_specs[key] = FilenameInput(
                        type="filename",
                        filename=source_spec.filename,
                        file_type=source_spec.file_type,
                        raw_yaml_key=spec.raw_yaml_key,
                    )  # Start with FilenameInput
                    resolved_specs[
                        key
                    ].transformation = spec.transform  # Add transformation attribute
                else:  # Should not happen if input is well-formed
                    raise TypeError(
                        f"TransformationSpec '{spec.raw_yaml_key}' source '{spec.source}' is not based on ValueSpec or FilenameSpec."
                    )
            else:
                raise KeyError(
                    f"TransformationSpec source '{spec.source}' for '{spec.raw_yaml_key}' not found."
                )
        else:
            resolved_specs[key] = spec  # Keep ValueSpec and FilenameSpec as they are

    return resolved_specs


def parse_yaml_to_specs(yaml_filepath: str) -> Dict[str, YamlInputSpec]:
    """
    Main function to parse YAML and return a dictionary of YamlInputSpecs.
    """
    yaml_config = parse_yaml_file(yaml_filepath)  # opens raw yaml -> dict
    yaml_specs = classify_yaml_specs(yaml_config)
    check_cached_specs(yaml_specs)
    resolved_specs = resolve_cached_specs(yaml_specs)
    return resolved_specs
