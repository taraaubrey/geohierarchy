from .registry import input_type_registry
from .definitions import (
    ValueInput,
    FilenameInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
)

# Register inputs
input_type_registry.register("value", ValueInput)
input_type_registry.register("filename", FilenameInput)
input_type_registry.register("cached", CachedInput)
input_type_registry.register("python_module", PythonModuleInput)
input_type_registry.register("multi", MultiInput)
