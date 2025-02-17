from geoconfig.main_config.UserConfig import UserConfig
from geoconfig.main_config.SchemaConfig import SchemaConfig

# user input
yaml_filepath = r"examples/example_input.yaml"

# new file
schema_filepath = r"src\geoconfig\settings\input_schema.yaml"
# will be encapsulated in an api eventually

# load specs
main_spec = UserConfig.from_filepath(yaml_filepath)
schema = SchemaConfig.from_filepath(schema_filepath)

# validate high level specs
main_spec.validate(schema)

# open model specific specs
# get model type
model_type = main_spec.get_model_type()
# get model schema
model_schemas = {
    'mf6': r'examples\model_schemas\mf6_schema.yaml',
}
mf6_schema_filepath = model_schemas[model_type]
mf6_schema = SchemaConfig.from_filepath(mf6_schema_filepath)
main_spec.validate(mf6_schema)


print("here")
