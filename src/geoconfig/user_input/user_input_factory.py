from typing import Dict, Union
from .input_types import (
    YamlInputSpec,
    RecursiveType,
    ValueInput,
    FilepathInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
    MathInput,
)

class UserInputFactory:
    def __init__(self):
        self._registery: Dict[str, YamlInputSpec] = {}
        self._default: YamlInputSpec = None
    
    def register(self, name: str, definition: YamlInputSpec):
        # TODO: error checking
        self._registery[name] = definition

    def register_default(self, name: str, definition: YamlInputSpec):
        if self._default:
            raise ValueError("Default already set.")
        self._default = definition
    
    def get(self, name: str) -> Union[YamlInputSpec, None]:
        return self._registery[name]

    def list_all(self) -> Dict[str, YamlInputSpec]:
        all_types = self._registery.copy()
        all_types.update({self._default.type: self._default})
        return all_types
    
    def create(self, value):
        for input_type in self._registery.values():
            if input_type.is_type(value):
                return input_type.create(value)

        return self._default.create(value)
    
    def resolve_if_recursive(self, input_spec: YamlInputSpec):
        if isinstance(input_spec, RecursiveType):
            for arg in input_spec.arg_values:
                arg = self.create(arg)
                input_spec.update_args(arg)
            return input_spec
        else:
            return input_spec


user_input_factory = UserInputFactory()  

# set default
user_input_factory.register_default("value", ValueInput)

# Register valid types of inputs in the yaml file
user_input_factory.register("filepath", FilepathInput)
user_input_factory.register("cached", CachedInput)
user_input_factory.register("python_module", PythonModuleInput)
user_input_factory.register("multi", MultiInput)
user_input_factory.register("math", MathInput)