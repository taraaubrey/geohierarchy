from geoconfig.main_config.UserConfig import UserConfig


#excel file
filepath = r"C:\Users\rccuser\Documents\a_data\dem_rasters\HBRC_dem_2020.tif"

user_input_filepath = r'examples\example_input.yaml'

model_input = UserConfig.from_filepath(filepath=user_input_filepath)



print('here')
