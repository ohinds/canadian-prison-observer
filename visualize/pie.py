import argparse
from collections import defaultdict
import os
import sys

import pandas as pd
import yaml

from ingest import statcan


class Pie:
    def __init__(self, pie_name, year=None):
        self.name = pie_name
        self.year = year
        self.config = yaml.load(
            open(os.path.join(os.path.dirname(__file__), pie_name + '.yaml')))
        self.levels = defaultdict(dict)
        self.table_cache = {}

    def build(self, base_config=None, level=0):
        """This function should build a tree
        """
        if level == 0:
            self.levels[0] = {'total':
                              self.build(base_config=self.config, level=1)}
            return

        total_sum = 0
        for name, conf in base_config.items():
            this_part_sum = 0
            for part in conf.get('parts', []):
                this_part_sum += self.build(base_config=part, level=level + 1)

            if 'statcan_id' in conf:
                table = self._get_table(conf['statcan_id'])
                mask = pd.Series(True, index=table.index)
                for column, val in conf.get('column constraints', {}).items():
                    mask &= table[column] == val
                value = table.loc[mask & (table.REF_DATE == self.year)].VALUE
                this_part_sum += value.item()

            self.levels[level][name] = this_part_sum
            total_sum += this_part_sum

        return total_sum

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
