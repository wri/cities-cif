import osmnx as ox

from .layer import Layer


class OpenStreetMap(Layer):
    def __init__(self, osm_tag=None, **kwargs):
        super().__init__(**kwargs)
        self.osm_tag = osm_tag

    def get_data(self, bbox):
        north, south, east, west = bbox[3],  bbox[1], bbox[0], bbox[2]
        osm_feature = ox.features_from_bbox(north, south, east, west, self.osm_tag)

        # Drop points
        osm_feature = osm_feature[osm_feature.geom_type != 'Point']

        # Keep LineString for Roads Class
        if 'highway' not in self.osm_tag:
            # Drop lines
            osm_feature = osm_feature[osm_feature.geom_type != 'LineString']

        # keep only columns desired to reduce file size 
        osm_feature = osm_feature.reset_index().loc[:, ['osmid','geometry']]

        return osm_feature
    
    def write(self, output_path):
        self.data['bbox'] = str(self.data.total_bounds)
        self.data['osm_tag'] = str(self.osm_tag)

        # Write to a GeoJSON file
        self.data.to_file(output_path, driver='GeoJSON')
