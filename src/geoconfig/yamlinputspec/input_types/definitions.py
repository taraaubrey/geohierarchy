import os  # Import for file existence checks
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Union, List

# import abstract class ABC
from abc import ABC, abstractmethod

# --- YamlInputSpec Classes ---
@dataclass
class YamlInputSpec(ABC):
    """Base class for YAML input specifications."""

    type: str  # e.g., "value", "filename", "existing", "transformation"
    description: Optional[str] = None
    raw_yaml_key: Optional[str] = (
        None  # Keep track of the original YAML key for error messages
    )

    @abstractmethod
    def is_type(self, value: Any) -> bool:
        """Check if the value is an instance of this class."""
        pass

@dataclass
class ValueInput(YamlInputSpec):
    """Represents a simple value input (string, boolean, integer, float)."""

    type: str = "value"
    value: Any = None

    def is_type(self, value: Any) -> bool:
        return isinstance(value, (str, bool, int, float))


@dataclass
class FilenameInput(YamlInputSpec):
    """Represents a filename input (raster, csv, shapefile)."""

    type: str = "filename"
    filename: str = None
    file_type: Optional[str] = None

    def is_type(self, value: Any) -> bool:
        return os.path.isfile(value)


# complex ----------------------------------------
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
    
    def is_type(self, value: Any) -> bool:
        return value.split(":")[0] == "$"



@dataclass
class PythonModuleInput(YamlInputSpec):
    """Represents a transformation to be applied."""

    type: str = "python_module"
    module: str = None
    function: str = None
    args: List[YamlInputSpec] = field(default_factory=list)

    @staticmethod
    def is_type(value: Any) -> bool:
        if value.split(":")[0] == "$py":
            return True
        elif any(
            [char in value for char in ["+", "-", "*", "/"]]) and value.startswith("("):
            return True
        return False


@dataclass
class MultiInput(YamlInputSpec):
    """Represents a list of inputs."""

    type: str = "multi"
    values: List[YamlInputSpec] = field(default_factory=list)

    def is_type(self, value: Any) -> bool:
        return isinstance(value, list)