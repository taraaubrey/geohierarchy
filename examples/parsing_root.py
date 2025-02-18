from geoconfig.main_config.UserConfig import UserConfig


user_input_filepath = r'examples\example_input.yaml'

model_input = UserConfig.from_filepath(filepath=user_input_filepath)



print('here')
