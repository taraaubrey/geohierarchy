import os  # Import for file existence checks
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Union, List

# import abstract class ABC
from abc import ABC, abstractmethod

# import FileTypeFactory
from geoconfig.input_types.filepath.filetype_factory import FileTypeFactory, filetype_factory

# --- YamlInputSpec Classes ---
@dataclass
class YamlInputSpec(ABC):
    """Base class for YAML input specifications."""

    type: str  # e.g., "value", "filepath", "existing", "transformation"
    value: Any = None  # Value of the input

    @abstractmethod
    def is_type(value: Any) -> bool:
        """Check if the value is an instance of this class."""
        pass

    @abstractmethod
    def create(self, value):
        """Create an instance of this class."""
        pass

@dataclass
class ValueInput(YamlInputSpec):
    """Represents a simple value input (string, boolean, integer, float)."""
    type: str = "value"

    @staticmethod
    def is_type(value: Any) -> bool:
        return isinstance(value, (str, bool, int, float))
    
    @classmethod
    def create(cls, value):
        return cls(value=value)


@dataclass
class FilepathInput(YamlInputSpec):
    """Represents a filepath input (raster, csv, shapefile)."""

    type: str = "filepath"
    value: str = None
        
    def __post_init__(self):
        self.filepath = self.value
        self.file_ext = self.value.split(".")[-1]

    @staticmethod
    def is_type(value: Any) -> bool:
        return os.path.isfile(value)
    
    @classmethod
    def create(cls, value):
        return cls(value=value)
    
    def open(self):
        return filetype_factory.open(self.filepath)


@dataclass
class CachedInput(YamlInputSpec):
    """Represents a reference to an existing input defined elsewhere."""

    type: str = "cached"
    source: str = None  # Key of the existing input

    def __post_init__(self):
        # if source has a '.' then add a field attribute to store the key
        if "." in self.source:
            self.field_key = self.source.split(".")[1]
            self.source = self.source.split(".")[0]
        else:
            self.field_key = None
    
    @staticmethod
    def is_type(value: Any) -> bool:
        return value.split(":")[0] == "$"
    
    @classmethod
    def create(self, value):
        return self(value=value, source=value.split(":")[1])


# recursive classes ----------------------------------------
@dataclass
class RecursiveType(ABC):
    """Base class for recursive types."""

    arg_values: List[Any] = None
    args: List[YamlInputSpec] = field(default_factory=list)

    def update_args(self, arg):
        self.args.append(arg)


@dataclass
class PythonModuleInput(YamlInputSpec, RecursiveType):
    """Represents a transformation to be applied."""

    type: str = "python_module"
    module: str = None
    function: str = None

    @staticmethod
    def is_type(value: Any) -> bool:
        return value.split(":")[0] == "$py"
    
    @classmethod
    def create(cls, value):
        arg_values = value.split("(")[1].split(")")[0].replace(" ", "").split(",")
        module = value.split(":")[1].split("(")[0].split(".")[:-1]
        function = value.split(":")[1].split("(")[0].split(".")[-1]
        return cls(value=value, module=module, function=function, arg_values=arg_values)


@dataclass
class MathInput(YamlInputSpec, RecursiveType):
    """Represents a mathematical operation."""

    type: str = "math"
    operation: str = None

    @staticmethod
    def is_type(value: Any) -> bool:
        return any([char in value for char in ["+", "-", "*", "/"]]) and value.startswith("(")
    
    @classmethod
    def create(cls, value):
        # find the math symbols and split the string
        for char in ["+", "-", "*", "/"]:
            if char in value:
                arg_values = value.replace(" ", "").replace("(", "").replace(")", "").split(char)
                break
        # recursive for each item in the list
        return cls(value=value, operation=char, arg_values=arg_values)
    
    # old method
    def _determine_python_module(self, values):
        char = self.operation
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


@dataclass
class MultiInput(YamlInputSpec, RecursiveType):
    """Represents a list of inputs."""

    type: str = "multi"

    @staticmethod
    def is_type(value: Any) -> bool:
        return isinstance(value, list)
    
    @classmethod
    def create(cls, value):
        arg_values = value
        # recursive for each item in the list
        return cls(value=value, arg_values=arg_values)