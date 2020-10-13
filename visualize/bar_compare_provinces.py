import argparse
import json
import glob
import os
import sys

from visualize.graph import Graph


class BarCompareProvinces(Graph):
    graph_type = 'bar_compare_provinces'

    def build(self):
        table = self.statcan.get(self.data['statcan_id'])
        table = table.loc[~table[self.data['measure']].isin(self.data.get('remove_measures', []))]
        table = table.loc[~table.GEO.isin(self.data.get('remove_geo', []))]
        for constraint_column, contraint_value in self.data.get('column_constraints', {}).items():
            table = table.loc[table[constraint_column] == contraint_value]

        geos = table.GEO.sort_values().unique()
        years = table.REF_DATE.sort_values().unique()
        measures = table[self.data['measure']].unique()
        compute_rates = self.options.get('rates', False)
        self.json = {
            'name':  self.name,
            'counts': {year: {geo: {} for geo in geos} for year in years},
            'rates': {year: {geo: {} for geo in geos} for year in years},
        }
        for value in measures:
            counts = table.loc[table[self.data['measure']] == value].pivot('REF_DATE', 'GEO', 'VALUE')
            counts = counts.interpolate().fillna(-1)

            if self.options.get('rate_gender', False):
                res_pop = self._get_resident_pop(gender=value)
            else:
                res_pop = self._get_resident_pop()

            if compute_rates:
                rates = (100000 * counts / res_pop.loc[counts.index]).round(1)
                rates[(rates < 0) | (rates.isnull())] = 'null'

            counts[counts < 0] = 'null'

            for year in years:
                for geo in geos:
                    val = 'null'
                    if geo in counts.columns:
                        val = counts.loc[year, geo]
                    self.json['counts'][year][geo][value] = val

                    rate = 'null'
                    if compute_rates and geo in rates.columns:
                        rate = rates.loc[year, geo]
                    self.json['rates'][year][geo][value] = rate

        order = [
            'Yukon',
            'Northwest Territories',
            'Nunavut',
            'British Columbia',
            'Alberta',
            'Saskatchewan',
            'Manitoba',
            'Ontario',
            'Quebec',
            'New Brunswick',
            'Nova Scotia',
            'Newfoundland and Labrador',
            'Prince Edward Island',
        ]

        self.json['data'] = [
            {
                'year': year,
                'columns': measures.tolist(),
                'counts': [
                    {'name': key, **self.json['counts'][year][key]} for key in order
                ],
                'rates': [
                    {'name': key, **self.json['rates'][year][key]} for key in order
                ],
            } for year in self.json['counts'].keys()
        ]


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('bar_name', nargs='*', help="Bar name(s) to generate.")
    parser.add_argument('--out_dir', '-o', default='data', help="Folder to output to.")
    args = parser.parse_args()
    if not args.bar_name:
        args.bar_name = [
            graph.replace('.yaml', '')
            for graph in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'bar_compare_provinces', '*.yaml')))
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
