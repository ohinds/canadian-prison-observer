import argparse
import json
import glob
import os
import sys

import pandas as pd

from visualize.graph import Graph


class GraphCompareProvinces(Graph):
    graph_type = 'graph_compare_provinces'

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

            federal_regions = counts.columns[0].endswith('Region')
            if self.options.get('rate_gender', False):
                respop = self._get_resident_pop(gender=conf['column constraints']['Sex'], federal_regions=federal_regions)
            else:
                respop = self._get_resident_pop(federal_regions=federal_regions)
            if 'Northwest Territories including Nunavut' in counts.columns:
                counts = self._combine_nwt_nunavut(counts)
                respop = self._combine_nwt_nunavut(respop)

            counts = counts.interpolate().fillna(-1)
            if self.options['rates']:
                if 'Federal jurisdiction' in counts.columns:
                    respop['Federal jurisdiction'] = respop.Canada
                respop = respop[counts.columns]
                rates = (100000 * counts / respop.loc[counts.index]).round(1)
                rates[rates < 0] = 'null'
            else:
                rates = counts.copy()
                rates.loc[:, :] = 'null'

            counts[counts < 0] = 'null'

            self.json['data'].append({
                'name': name,
                'counts': [{'name': col, 'values': counts[col].values.tolist()} for col in counts.columns],
                'rates': [{'name': col, 'values': rates[col].values.tolist()} for col in rates.columns],
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


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('graph_name', nargs='*', help="Graph name(s) to generate.")
    parser.add_argument('--out_dir', '-o', default='data', help="Folder to output to.")
    args = parser.parse_args()
    if not args.graph_name:
        args.graph_name = [
            graph.replace('.yaml', '')
            for graph in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'graph_compare_provinces', '*.yaml')))
        ]

    graphs = []
    for graph_name in args.graph_name:
        graph = GraphCompareProvinces(graph_name)
        graph.build()
        graphs.append(graph.json)

    with open(os.path.join(args.out_dir, 'graph_compare_provinces.json'), 'w') as fp:
        json.dump(graphs, fp)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
