from typing import Dict
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
        self._default: ValueInput = None
    
    def register(self, name: str, definition: YamlInputSpec):
        # TODO: error checking
        self._registery[name] = definition

    def register_default(self, name: str, definition: YamlInputSpec):
        if self._default:
            raise ValueError("Default already set.")
        self._default = definition

    def get(self, value: str) -> Dict[str, type]:
        if value in self._registery:
            return self._registery[value]
        else:
            return self._default
   
    def classify_user_input(self, value: str) -> YamlInputSpec:
        usertype = self._get_type(value)

        if isinstance(usertype, RecursiveType):
            return self._resolve_if_recursive(usertype)
        else:
            return usertype
    
    def _get_type(self, value: str):
        for input_type in self._registery.values():
            if input_type.is_type(value):
                return input_type.create(value)

        return self._default.create(value)
    
    def _resolve_if_recursive(self, input_spec: YamlInputSpec):
        if isinstance(input_spec, RecursiveType):
            for arg in input_spec.arg_values:
                arg = self.classify_user_input(arg)
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
