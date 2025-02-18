from geoconfig.main_config.UserConfig import UserConfig
from geoconfig.main_config.SchemaConfig import SchemaConfig

from geoconfig.user_input.user_input_factory import UserInputFactory
from geoconfig.user_input.input_types import (
    ValueInput,
    FilepathInput,
    CachedInput,
    PythonModuleInput,
    MultiInput,
    MathInput,
)


user_input_filepath = r'examples\example_input.yaml'

# internal schemas
schema_filepaths = [r'src\geoconfig\settings\input_schema.yaml']

main_spec = UserConfig.from_filepath(filepath=user_input_filepath)

print('here')
