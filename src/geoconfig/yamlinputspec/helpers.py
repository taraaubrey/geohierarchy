
from typing import Any, Dict
from .YamlInputSpec_base import (
    YamlInputSpec,
    ValueInput,
    FilenameInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
)



    

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

    from geoconfig.yamlinputspec.yaml_spec_class import YamlSpec
    main_spec = YamlSpec.from_filename(yaml_filepath)

    # Create input_cache?

    check_cached_specs(yaml_specs)
    resolved_specs = resolve_cached_specs(yaml_specs)
    return resolved_specs
