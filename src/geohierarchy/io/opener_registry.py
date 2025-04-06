from geohierarchy.io.openers import GeotiffOpener, ShapefileOpener, CSVOpener

class OpenerRegistry:
    registry = {
        'geotiff': GeotiffOpener,
        'shapefile': ShapefileOpener,
        'csv': CSVOpener,
    }

    def get(self, filepath):
        ext = filepath.split('.')[-1]
        return self.registry.get(ext)