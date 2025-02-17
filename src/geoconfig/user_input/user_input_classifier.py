from .user_input_factory import user_input_factory

class UserInputClassifier:
    def __init__(self):
        # get registered spec types
        self.input_factory = user_input_factory
    
    def get_spec_type(self, value):
        return self._get_input_type_from_value(value)
   
    def _get_input_type_from_value(self, value):
        parsed_input = self.input_factory.create(value)
        return self.input_factory.resolve_if_recursive(parsed_input)