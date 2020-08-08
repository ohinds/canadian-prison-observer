import argparse
from collections import defaultdict
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import yaml

from ingest import statcan


class Pie:
    def __init__(self, pie_name, year=None):
        self.name = pie_name
        self.year = year
        self.config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), pie_name + '.yaml')))
        self.data = None
        self.table_cache = {}

    def build(self, parent_name: Optional[str] = None, parents: Optional[Dict] = None,
              config: Optional[Dict] = None):
        """Build a tree representation of the pie
        """
        if not config:
            self.leaves = []
            self.build(self.name, {}, config=self.config)
            self.data = pd.DataFrame(self.leaves)
            return

        for name, conf in config.items():
            if 'statcan_id' not in conf:
                dim_parents = parents.copy()
                dim_parents.update({parent_name: name})
                for dim_name, dim_conf in conf.items():
                    for part_name, part_conf in conf.items():
                        ours = dim_parents.copy()
                        ours.update({dim_name: part_name})
                        self.build(part_name, ours, part_conf)
            else:
                table = self._get_table(conf['statcan_id'])
                mask = pd.Series(True, index=table.index)
                for column, val in conf.get('column constraints', {}).items():
                    mask &= table[column] == val
                value = table.loc[mask & (table.REF_DATE == self.year)].VALUE.item()
                ours = parents.copy()
                ours.update({parent_name: name, 'count': value})
                self.leaves.append(ours)

    def get_figure(self):
        fig = px.sunburst(
            self.data, path=[c for c in self.data.columns if c != 'count'], values='count')
        fig.update_layout(height=900, font_family="Comic Sans MS")
        return fig

    def show(self):
        self.get_figure().show()

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
        pie.show()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
