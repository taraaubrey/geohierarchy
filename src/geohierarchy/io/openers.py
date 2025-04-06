from abc import ABC, abstractmethod

class Opener(ABC):
    @abstractmethod
    def open(self):
        pass

class GeotiffOpener(Opener):
    def __init__(self):
        self.type = 'geotiff'

    def open(self, filepath, **kwargs):
        print('accessing geotiff opener')
        pass

class ShapefileOpener(Opener):
    def __init__(self):
        self.type = 'shapefile'

    def open(self, filepath, **kwargs):
        print('accessing shapefile opener')
        pass

class CSVOpener(Opener):
    def __init__(self):
        self.type = 'csv'

    def open(self, filepath, **kwargs):
        print('accessing csv opener')
        pass