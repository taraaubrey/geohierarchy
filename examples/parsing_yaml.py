from geoconfig.main_config.input_config import InputConfig

yaml_filepath = "examples/example_input.yaml"
# will be encapsulated in an api eventually

main_spec = InputConfig.from_filepath(yaml_filepath)

print("here")
