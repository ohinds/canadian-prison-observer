import os

import yaml

from ingest.statcan import StatCan


class Graph:
    def __init__(self, graph_name):
        yaml_config = yaml.safe_load(
            open(os.path.join(os.path.dirname(__file__), self.graph_type, graph_name + '.yaml')))

        self.name = yaml_config['name']
        self.options = yaml_config.get('options', {})
        self.data = yaml_config['data']
        self.statcan = StatCan()

    def _get_resident_pop(self, federal_regions=False, gender='Both sexe', age='All ages'):
        gender = gender + 's'
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
