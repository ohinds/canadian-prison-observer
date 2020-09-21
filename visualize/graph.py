import os

import yaml

from ingest.statcan import StatCan


class Graph:
    def __init__(self, graph_name):
        yaml_config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), self.graph_type, graph_name + '.yaml')))

        self.name = yaml_config['name']
        self.options = yaml_config.get('options', {})
        self.data = yaml_config['data']
        self.statcan = StatCan()
