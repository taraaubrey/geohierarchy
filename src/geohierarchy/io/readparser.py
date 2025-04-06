from geohierarchy.input import InputObject
from os import path

class ReadParser:
    def __init__(self, path):
        self.path = path

    def read(input_list, mask, clip):
        # TODO: check list

        data_list = []
        for f in input_list:
            if isinstance(f, str) and path.isfile(f):
                input = InputObject(f, mask, clip)
            elif isinstance(f, dict):
                input = InputObject(dict)

            data = input.open()

        ## combine xr array