from typing import Dict, Any
from os.path import isfile

from geoconfig.input_types.input_factory import input_factory

class SpecTypeClassifier:
    def __init__(self):
        # get registered spec types
        self.input_factory = input_factory
    
    def get_spec_type(self, value):
        return self._get_input_type_from_value(value)
   
    def _get_input_type_from_value(self, value):
        parsed_input = self.input_factory.create(value)
        return self.input_factory.resolve_if_recursive(parsed_input)
        

def get_value_spec_type(value):
    classifier = SpecTypeClassifier()
    return classifier.get_spec_type(value)