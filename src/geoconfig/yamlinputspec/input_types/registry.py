from typing import Dict, Union
from .definitions import YamlInputSpec

class InputTypeRegistry:
    def __init__(self):
        self._registery: Dict[str, YamlInputSpec] = {}
    
    def register(self, name: str, definition: YamlInputSpec):
        # TODO: error checking
        self._registery[name] = definition
    
    def get(self, name: str) -> Union[YamlInputSpec, None]:
        return self._registery[name]

    def list_all(self) -> Dict[str, YamlInputSpec]:
        return self._registery

input_type_registry = InputTypeRegistry()