from abc import ABC, abstractmethod
from os.path import isfile

from ..settings.config import (
    upstream_model_keys,
    model_type_key,
    )

from ..user_input.user_input_factory import UserInputFactory, user_input_factory
from ..user_input.input_types import FilepathInput


class InputConfig(ABC):
    def __init__(self, filepath: str, filespec: FilepathInput):
        self._user_input_factory: UserInputFactory = user_input_factory
        self._upstream_model_keys = upstream_model_keys
        self._model_type_key = model_type_key

        if filespec:
            self.filespec = filespec
            self.filepath = self.filespec.filepath
        elif filepath:
            self.filespec = self._user_input_factory.classify_user_input(filepath)
            if not isfile(self.filespec.value):
                raise FileNotFoundError(f"File not found: {self.filespec.value}")
            self.filepath = filepath
        else:
            raise ValueError("Must provide either a filepath or a filespec.")

        self.input_dict = self.filespec.open()

    def __repr__(self):
        return f"{__class__.__name__}({self.filepath})"
    
    @abstractmethod
    def from_filepath(cls, filepath:str):
        return cls(filepath=filepath, filespec=None)
    
    @abstractmethod
    def from_filespec(cls, filespec:FilepathInput):
        return cls(filespec=filespec, filepath=None)
    
