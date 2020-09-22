import argparse
import json
import glob
import os
import sys

import pandas as pd

from visualize.graph import Graph


class BarCompareProvinces(Graph):
    graph_type = 'bar_compare_provinces'

    def build(self):
        table = self.statcan.get(self.data['statcan_id'])
        table = table.loc[~table[self.data['measure']].isin(self.data.get('remove_measures', []))]
        table = table.loc[~table.GEO.isin(self.data.get('remove_geos', []))]
        for constraint_column, contraint_value in self.data.get('column_constraints', {}).items():
            table = table.loc[table[constraint_column] == contraint_value]

        geos = table.GEO.sort_values().unique()
        years = table.REF_DATE.sort_values().unique()
        self.json = {
            'name':  self.name,
            'data': {year: {geo: {} for geo in geos} for year in years},
        }
        for value in table[self.data['measure']].unique():
            counts = table.loc[table[self.data['measure']] == value].pivot('REF_DATE', 'GEO', 'VALUE')
            counts = counts.interpolate().fillna('null')
            for year in years:
                for geo in geos:
                    val = 'null'
                    if geo in counts.columns:
                        val = counts.loc[year, geo]
                    self.json['data'][year][geo][value] = val

        self.json['data'] = [
            {
                'year': year, 'data': [
                    {'name': key, **val} for key, val in self.json['data'][year].items()
                ]
            }
            for year in self.json['data'].keys()
        ]

    def _combine_nwt_nunavut(self, counts):
        counts['Northwest Territories including Nunavut'] = \
            counts['Northwest Territories including Nunavut'].fillna(0) + \
            counts['Northwest Territories'].fillna(0) + \
            counts['Nunavut'].fillna(0)
        del counts['Northwest Territories']
        del counts['Nunavut']

        return counts

    def _get_resident_pop(self, federal_regions=False):
        respop = self.statcan.get_resident_pop().copy()
        respop = respop.loc[(respop.Sex == 'Both sexes') & (respop['Age group'] == 'All ages')]
        respop['REF_DATE'] = (respop.REF_DATE - 1).astype(str) + '/' + respop.REF_DATE.astype(str)
        respop = respop.pivot('REF_DATE', 'GEO', 'VALUE')

        if federal_regions:
            region_map = {
                'Atlantic Region': [
                    'New Brunswick',
                    'Newfoundland and Labrador',
                    'Nova Scotia',
                    'Prince Edward Island',
                ],
                'Ontario Region': [
                    'Nunavut',
                    'Ontario',
                ],
                'Pacific Region': [
                    'British Columbia',
                    'Yukon',
               ],
                'Prairie Region': [
                    'Alberta',
                    'Saskatchewan',
                    'Manitoba',
                    'Northwest Territories',
                ],
                'Quebec Region': [
                    'Quebec'
                ],
            }

            for region, provinces in region_map.items():
                respop[region] = respop[provinces].sum(axis=1)
                for province in provinces:
                    del respop[province]

        return respop


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('bar_name', nargs='*', help="Bar name(s) to generate.")
    parser.add_argument('--out_dir', '-o', default='data', help="Folder to output to.")
    args = parser.parse_args()
    if not args.bar_name:
        args.bar_name = [
            graph.replace('.yaml', '')
            for graph in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'graph_within_province', '*.yaml')))
        ]

    bars = []
    for bar_name in args.bar_name:
        bar = BarCompareProvinces(bar_name)
        bar.build()
        bars.append(bar.json)

    with open(os.path.join(args.out_dir, 'bar_compare_provinces.json'), 'w') as fp:
        json.dump(bars, fp)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
