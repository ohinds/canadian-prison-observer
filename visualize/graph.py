import argparse
import json
import glob
import os
import sys

import pandas as pd
import yaml

from ingest.statcan import StatCan


class Graph:
    def __init__(self, graph_name):
        yaml_config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), 'graph', graph_name + '.yaml')))
        self.name = yaml_config['name']
        self.options = yaml_config.get('options', {})
        self.data = yaml_config['data']
        self.statcan = StatCan()

    def build(self):
        self.json = {'name': self.name, 'data': []}
        for name, conf in self.data.items():
            table = self.statcan.get(conf['statcan_id'])
            mask = pd.Series(True, index=table.index)
            for column, val in conf.get('column constraints', {}).items():
                mask &= table[column] == val
            counts = table.loc[mask].pivot('REF_DATE', 'GEO', 'VALUE')

            if 'remove geo' in conf:
                del counts[conf['remove geo']]

            respop = self._get_resident_pop(federal_regions=counts.columns[0].endswith('Region'))
            if 'Northwest Territories including Nunavut' in counts.columns:
                counts = self._combine_nwt_nunavut(counts)
                respop = self._combine_nwt_nunavut(respop)

            counts = counts.interpolate().fillna(-1)
            if self.options['rates']:
                respop = respop[counts.columns]
                rates = 100000 * counts / respop.loc[counts.index]
                rates[rates < 0] = 'null'

            counts[counts < 0] = 'null'

            self.json['data'].append({
                'name': name,
                'counts': [{'name': col, 'values': counts[col].values.tolist()} for col in counts.columns],
                'rates': [{'name': col, 'values': rates[col].values.tolist()} for col in rates.columns] if self.options['rates'] else 'null',
                'dates': counts.index.values.tolist()
            })

    def _combine_nwt_nunavut(self, counts):
        counts['Northwest Territories including Nunavut'] = \
            counts['Northwest Territories including Nunavut'].fillna(0) + \
            counts['Northwest Territories'].fillna(0) + \
            counts['Nunavut'].fillna(0)
        del counts['Northwest Territories']
        del counts['Nunavut']

        return counts

    def _get_resident_pop(self, federal_regions=False):
        respop = self.statcan.get_resident_pop()
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
                respop[region] = respop[provinces].sum()
                for province in provinces:
                    del respop[province]

        return respop


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
