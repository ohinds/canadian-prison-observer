import argparse
import os
import sys
from typing import Dict

import pandas as pd
import plotly.express as px
import yaml

from ingest import statcan


class PieBuildError(Exception):
    """
    """


class Pie:
    def __init__(self, pie_name):
        self.name = pie_name
        self.config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), pie_name + '.yaml')))
        self.data = None
        self.table_cache = {}

    def build(self, year='2017/2018'):
        """Build a tree representation of the pie
        """
        self.leaves = []
        self._build(year, self.name, {}, config=self.config)
        self.data = pd.DataFrame(self.leaves)

    def _build(self, year: str, parent_name: str, parents: Dict, config: Dict):
        for name, conf in config.items():
            if 'statcan_id' not in conf:
                dim_parents = parents.copy()
                dim_parents.update({parent_name: name})
                for dim_name, dim_conf in conf.items():
                    for part_name, part_conf in conf.items():
                        ours = dim_parents.copy()
                        ours.update({dim_name: part_name})
                        self._build(year, part_name, ours, part_conf)
            else:
                table = self._get_table(conf['statcan_id'])
                if not table.REF_DATE.isin([year]).any():
                    raise PieBuildError(f"Year [{year}] not found in statcan_id {conf['statcan_id']}")
                mask = pd.Series(True, index=table.index)
                for column, val in conf.get('column constraints', {}).items():
                    mask &= table[column] == val

                try:
                    value = table.loc[mask & (table.REF_DATE == year)].VALUE.item()
                except:
                    PieBuildError(f"Failed to find a single value for {conf}.")
                ours = parents.copy()
                ours.update({parent_name: name, 'count': value})
                self.leaves.append(ours)

    def get_figure(self):
        categories = [c for c in self.data.columns if c != 'count']
        hover_data = {category: f"%{category}" for category in categories}
        hover_data.update({
            'count': 'count',
        })
        fig = px.sunburst(
            self.data, values='count', path=categories, hover_data=hover_data, height=800)
        fig.update_layout(font_size=20)
        fig['data'][0]['hovertemplate'] = '%{id}<br>Average Daily Population %{customdata[4]}'
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
        pie = Pie(pie_name)
        pie.build(year=args.year)
        pie.show()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
