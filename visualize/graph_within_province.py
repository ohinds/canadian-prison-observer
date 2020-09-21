import argparse
import json
import glob
import os
import sys

from visualize.graph import Graph


class GraphWithinProvince(Graph):
    graph_type = 'graph_within_province'

    def build(self):
        table = self.statcan.get(self.data['statcan_id'])
        self.json = {
            'name':  self.name,
            'data': []
        }

        for geo in sorted(table.GEO.unique()):
            if geo in self.data['remove_geo']:
                continue

            mask = table.GEO == geo
            for constraint_column, contraint_value in self.data.get('column_constraints', {}).items():
                mask &= table[constraint_column] == contraint_value

            for remove_measure in self.data.get('remove_measures', []):
                mask &= table[self.data['measure']] != remove_measure

            counts = table.loc[mask].pivot('REF_DATE', self.data['measure'], 'VALUE')
            counts = counts.interpolate().fillna('null')
            self.json['data'].append({
                'name': geo,
                'counts': [{'name': col, 'values': counts[col].values.tolist()} for col in counts.columns],
                'dates': counts.index.values.tolist()
            })


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('graph_name', nargs='*', help="Graph name(s) to generate.")
    parser.add_argument('--out_dir', '-o', default='data', help="Folder to output to.")
    args = parser.parse_args()
    if not args.graph_name:
        args.graph_name = [
            graph.replace('.yaml', '')
            for graph in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'graph_within_province', '*.yaml')))
        ]

    graphs = []
    for graph_name in args.graph_name:
        graph = GraphWithinProvince(graph_name)
        graph.build()
        graphs.append(graph.json)

    with open(os.path.join(args.out_dir, 'graph_within_province.json'), 'w') as fp:
        json.dump(graphs, fp)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
