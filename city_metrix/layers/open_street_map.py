import osmnx as ox

from .layer import Layer


class OpenStreetMap(Layer):
    def __init__(self, osm_tag=None, **kwargs):
        super().__init__(**kwargs)
        self.osm_tag = osm_tag

    def get_data(self, bbox):
        north, south, east, west = bbox[3],  bbox[1], bbox[0], bbox[2]
        osm_feature = ox.features_from_bbox(north, south, east, west, self.osm_tag)

        # Filter out Point and LineString (if 'highway' not in tags)
        if 'highway' not in self.osm_tag:
            osm_feature = osm_feature[osm_feature.geom_type.isin(['Polygon', 'MultiPolygon'])]
        else:
            osm_feature = osm_feature[osm_feature.geom_type != 'Point']

        # keep only columns desired to reduce file size
        keep_col = ['osmid', 'geometry']
        for key in self.osm_tag:
            if key in osm_feature.columns:
                keep_col.append(key)
        # keep 'lanes' for 'highway'
        if 'highway' in keep_col and 'lanes' in osm_feature.columns:
            keep_col.append('lanes')
        osm_feature = osm_feature.reset_index()[keep_col]

        return osm_feature

    def write(self, output_path):
        self.data['bbox'] = str(self.data.total_bounds)
        self.data['osm_tag'] = str(self.osm_tag)

        # Write to a GeoJSON file
        self.data.to_file(output_path, driver='GeoJSON')
