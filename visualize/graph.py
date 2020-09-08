import argparse
import json
import glob
import os
import sys

import pandas as pd
import yaml

from ingest import statcan


class Graph:
    def __init__(self, graph_name):
        yaml_config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), 'graph', graph_name + '.yaml')))
        self.name = yaml_config['name']
        self.config = yaml_config['config']
        self.table_cache = {}

    def build(self):
        self.json = {'name': self.name, 'data': {}}
        for name, conf in self.config.items():
            table = self._get_table(conf['statcan_id'])
            mask = pd.Series(True, index=table.index)
            for column, val in conf.get('column constraints', {}).items():
                mask &= table[column] == val
            pivot = table.loc[mask].pivot('REF_DATE', 'GEO', 'VALUE')
            if 'Northwest Territories including Nunavut' in pivot.columns:
                pivot['Northwest Territories including Nunavut'] = \
                    pivot['Northwest Territories including Nunavut'].fillna(0) + \
                    pivot['Northwest Territories'].fillna(0) + \
                    pivot['Nunavut'].fillna(0)
                del pivot['Northwest Territories']
                del pivot['Nunavut']
            pivot = pivot.interpolate()
            self.json['data'][name] = pivot.to_json()

    def _get_table(self, statcan_id):
        if statcan_id not in self.table_cache:
            self.table_cache[statcan_id] = statcan.get_table(statcan_id)
        return self.table_cache[statcan_id]


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('graph_name', nargs='*', help="Graph name(s) to generate.")
    parser.add_argument('--out_dir', '-o', default='data', help="Folder to output to.")
    args = parser.parse_args()
    if not args.graph_name:
        args.graph_name = [
            graph.replace('.yaml', '')
            for graph in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'graph', '*.yaml')))
        ]

    graphs = []
    for graph_name in args.graph_name:
        graph = Graph(graph_name)
        graph.build()
        graphs.append(graph.json)

    with open(os.path.join(args.out_dir, 'graphs.json'), 'w') as fp:
        json.dump(graphs, fp)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
