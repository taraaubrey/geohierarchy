from abc import ABC
from .InputConfig import InputConfig

from ..user_input.input_types import FilepathInput


class UserConfig(InputConfig):
    def __init__(
            self,
            filepath: str,
            filespec: FilepathInput,
            set_upstream: bool = True):
        super().__init__(filepath=filepath, filespec=filespec)

        self._flatspecs = self._classify_user_inputs(self.input_dict)
        self._specs = self._flat_to_nested(self._flatspecs)

        if set_upstream:
            self._upstream_specs = self._set_upstream_specs(keys = self._upstream_model_keys)
        else:
            self._upstream_specs = None

    @property
    def specs(self):
        return self._specs
    
    @property
    def upstream_specs(self):
        if self._upstream_specs is None:
            print('Upstream specs not set.')
        return self._upstream_specs
    
    @classmethod
    def from_filepath(cls, filepath: str, set_upstream: bool=True):
        return cls(filepath=filepath, filespec=None, set_upstream=set_upstream)
    
    @classmethod
    def from_filespec(cls, filespec: FilepathInput, set_upstream: bool=True):
        return cls(filespec=filespec, filepath=None, set_upstream=set_upstream)
    
    #move to helper
    def _get_nested_value_iterative(self, nested_dict, keys) -> dict:
        """
        Retrieves a value from a nested dictionary using a list of keys.

        Args:
            nested_dict (dict): The nested dictionary.
            keys (list): A list of keys representing the path to the value.

        Returns:
            The value at the nested path, or None if any key is not found.
        """
        current_level = nested_dict.copy()
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]  # Move to the next level
            else:
                return None  # Key not found at this level, or current_level is not a dict
        return current_level # Return the value at the final level (or None if we returned early)

    
    def _set_upstream_specs(self, keys:list):
        other_yamls = self._get_nested_value_iterative(self.specs, keys)

        self._validate_hierarchy(other_yamls)
        
        hier_inputs = []
        for i, filespec in other_yamls.items():
            new_input = self.from_filespec(filespec=filespec, set_upstream=False)
            hier_inputs.append(new_input)

        return hier_inputs
   
    def _classify_user_inputs(self, yaml_config: dict, parent_key_prefix: str = ""):
        yaml_specs = {}
        for key, value in yaml_config.items():
            raw_yaml_key = key if not parent_key_prefix else f"{parent_key_prefix}.{key}"

            # Recursive call for nested structures
            if isinstance(value, dict):
                yaml_update = self._classify_user_inputs(value, parent_key_prefix=raw_yaml_key)
                yaml_specs.update(yaml_update)
            else:
                yaml_specs[raw_yaml_key] = self._user_input_factory.classify_user_input(value)
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

    def _validate_hierarchy(self, other_yamls:dict):
        h_counter = 0

        for key, model_yamlinput in other_yamls.items():
            hlevel = int(key)

            # Check if the key is a valid hierarchy level
            if hlevel != h_counter:
                raise ValueError(f"Invalid hierarchy level: {hlevel}. Expected: {h_counter}")
            h_counter += 1 

    