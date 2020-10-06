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
        res_pop = self._get_resident_pop()
        self.json = {
            'name':  self.name,
            'counts': {year: {geo: {} for geo in geos} for year in years},
            'rates': {year: {geo: {} for geo in geos} for year in years},
        }
        for value in measures:
            counts = table.loc[table[self.data['measure']] == value].pivot('REF_DATE', 'GEO', 'VALUE')
            counts = counts.interpolate().fillna(-1)

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

        self.json['data'] = [
            {
                'year': year,
                'columns': measures.tolist(),
                'counts': [
                    {'name': key, **val} for key, val in self.json['counts'][year].items()
                ],
                'rates': [
                    {'name': key, **val} for key, val in self.json['rates'][year].items()
                ],
            } for year in self.json['counts'].keys()
        ]

    def _get_resident_pop(self, federal_regions=False, gender='Both sexes', age='All ages'):
        respop = self.statcan.get_resident_pop().copy()
        respop = respop.loc[(respop.Sex == gender) & (respop['Age group'] == age)]
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
