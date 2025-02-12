import yaml
import os  # Import for file existence checks
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Union, List


# --- YamlInputSpec Classes ---
@dataclass
class YamlInputSpec:
    """Base class for YAML input specifications."""

    type: str  # e.g., "value", "filename", "existing", "transformation"
    description: Optional[str] = None
    raw_yaml_key: Optional[str] = (
        None  # Keep track of the original YAML key for error messages
    )


@dataclass
class ValueInput(YamlInputSpec):
    """Represents a simple value input (string, boolean, integer, float)."""

    type: str = "value"
    value: Any = None


@dataclass
class FilenameInput(YamlInputSpec):
    """Represents a filename input (raster, csv, shapefile)."""

    type: str = "filename"
    filename: str = None
    file_type: Optional[str] = None


# complex ----------------------------------------
@dataclass
class CachedInput(YamlInputSpec):
    """Represents a reference to an existing input defined elsewhere."""

    type: str = "cached"
    source: str = None  # Key of the existing input


@dataclass
class PythonModuleInput(YamlInputSpec):
    """Represents a transformation to be applied."""

    type: str = "python_module"
    module: str = None
    function: str = None
    args: List[YamlInputSpec] = field(default_factory=list)


@dataclass
class MultiInput(YamlInputSpec):
    """Represents a list of inputs."""

    type: str = "multi"
    values: List[YamlInputSpec] = field(default_factory=list)


@dataclass
class DictInput(YamlInputSpec):
    """Represents a dictionary of inputs."""

    type: str = "dict"
    values: Dict[str, YamlInputSpec] = field(default_factory=dict)