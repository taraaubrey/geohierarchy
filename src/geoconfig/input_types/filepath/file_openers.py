from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class FileOpener(ABC):
    @abstractmethod
    def open(filepath, opener_kwargs):
        pass


@dataclass
class YamlOpener(FileOpener):

    def open(filepath, opener_kwargs=None):
        from yaml import load, BaseLoader

        with open(filepath, "r") as file:
            return load(file, Loader=BaseLoader)

@dataclass
class RasterOpener(FileOpener):
    def open(self, opener_kwargs=None):
        pass

@dataclass
class ShapefileOpener(FileOpener):
    def open(self, opener_kwargs=None):
        pass

@dataclass
class NetCDFOpener(FileOpener):
    def open(self, opener_kwargs=None):
        pass

@dataclass
class CSVOpener(FileOpener):
    def open(self, opener_kwargs=None):
        pass