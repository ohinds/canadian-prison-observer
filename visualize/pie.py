import argparse
from collections import defaultdict
import os
import sys
from typing import Dict, List, Optional

import attr
import numpy as np
import pandas as pd
import yaml

from ingest import statcan


@attr.s(auto_attribs=True)
class Node():
    name: str
    count: Optional[int] = 0
    proportion: Optional[float] = np.nan
    children: Optional[List] = attr.Factory(list)

    def add_child(self, child):
        self.children.append(child)
        self.count += child.count


class Pie:
    def __init__(self, pie_name, year=None):
        self.name = pie_name
        self.year = year
        self.config = yaml.load(
            open(os.path.join(os.path.dirname(__file__), pie_name + '.yaml')))
        self.table_cache = {}

    def build(self, node_name: Optional[str] = None, node_config: Optional[Dict] = None):
        """Build a tree representation of the pie
        """
        if not node_config:
            self.tree = self.build(self.name, node_config=self.config)
            return

        node = Node(name=node_name)
        for name, conf in node_config.items():
            if 'statcan_id' not in conf:
                node.add_child(self.build(name, conf))
            else:
                table = self._get_table(conf['statcan_id'])
                mask = pd.Series(True, index=table.index)
                for column, val in conf.get('column constraints', {}).items():
                    mask &= table[column] == val
                value = table.loc[mask & (table.REF_DATE == self.year)].VALUE.item()
                node.add_child(Node(name=name, count=value))
        return node

    def _get_table(self, statcan_id):
        if statcan_id not in self.table_cache:
            self.table_cache[statcan_id] = statcan.get_table(statcan_id)
        return self.table_cache[statcan_id]


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('pie_name', nargs='+', help="Pie name(s) to generate.")
    parser.add_argument('--year', '-y', default='2017/2018',
                        help="Year to generate pie for (default is latest).")
    args = parser.parse_args()

    for pie_name in args.pie_name:
        pie = Pie(pie_name, year=args.year)
        pie.build()
        breakpoint()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
