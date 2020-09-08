import argparse
import json
import glob
import os
import sys
from typing import Dict, List, Optional

import attr
import pandas as pd
import yaml

from ingest import statcan


@attr.s(auto_attribs=True)
class Node():
    name: str
    values: Optional[Dict[str, float]] = None
    children: Optional[List] = attr.Factory(list)

    def add_child(self, child):
        self.children.append(child)

    def extract_year(self, year):
        if self.values:
            return {'name': self.name, 'value': self.values[year] if year in self.values else None}

        return {
            'name': self.name,
            'children': [c.extract_year(year) for c in self.children]
        }


class Pie:
    def __init__(self, pie_name):
        yaml_config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), 'pie', pie_name + '.yaml')))
        self.name = yaml_config['name']
        self.years = set()
        self.config = yaml_config['config']
        self.table_cache = {}

    def build(self):
        self.tree = self._build_tree('root', node_config=self.config)
        self.json = {'name': self.name, 'data': {}}
        for year in sorted(self.years):
            self.json['data'][year] = self.tree.extract_year(year)

    def _build_tree(self, node_name: Optional[str] = None, node_config: Optional[Dict] = None):
        """Build a tree representation of the pie
        """
        node = Node(name=node_name)
        for name, conf in node_config.items():
            if 'statcan_id' not in conf:
                node.add_child(self._build_tree(name, conf))
            else:
                table = self._get_table(conf['statcan_id'])
                mask = pd.Series(True, index=table.index)
                for column, val in conf.get('column constraints', {}).items():
                    mask &= table[column] == val
                values = table.loc[mask].set_index('REF_DATE').VALUE.fillna('null')
                self.years |= set(values.index.values)

                # TODO add interpolation here
                node.add_child(Node(name=name, values=values.to_dict()))
        return node

    def _get_table(self, statcan_id):
        if statcan_id not in self.table_cache:
            self.table_cache[statcan_id] = statcan.get_table(statcan_id)
        return self.table_cache[statcan_id]


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('pie_name', nargs='*', help="Pie name(s) to generate.")
    parser.add_argument('--out_dir', '-o', default='data', help="Folder to output to.")
    args = parser.parse_args()
    if not args.pie_name:
        args.pie_name = [
            pie.replace('.yaml', '')
            for pie in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'pie', '*.yaml')))
        ]

    pies = []
    for pie_name in args.pie_name:
        pie = Pie(pie_name)
        pie.build()
        pies.append(pie.json)

    with open(os.path.join(args.out_dir, 'pies.json'), 'w') as fp:
        json.dump(pies, fp)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
