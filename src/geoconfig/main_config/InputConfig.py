from abc import ABC
from ..user_input.user_input_classifier import UserInputClassifier


class InputConfig(ABC):
    def __init__(self, filepath=None, filespec=None):
        self._UserInputClassifier = UserInputClassifier()
        self._types_of_input = self._UserInputClassifier.input_factory.list_all()

        self.get_spec_type = self._UserInputClassifier.get_spec_type

        if filespec:
            self.filespec = filespec
        elif filepath:
            self.filespec = self.get_spec_type(filepath)

        self.input_dict = self.filespec.open()

    def __repr__(self):
        return f"{__class__.__name__}({self.filepath})"
    
    @classmethod
    def from_filepath(cls, filepath):
        return cls(filepath=filepath)
    
    @classmethod
    def from_spec(cls, filespec):
        return cls(filespec=filespec)
