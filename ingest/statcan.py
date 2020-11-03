import io
import json
import requests
import sys
import zipfile

import pandas as pd


class StatCanDownloadError(Exception):
    pass


STATCAN_IDS = {
    35100013: {
        'name': 'Operating expenditures for adult correctional services',
        'targets': ['Operating expenditures'],
        'constraints': {
            'UOM': 'Current dollars',
            'SCALAR_FACTOR': 'thousands',
        },
    },
    35100014: {
        'name': 'Adult admissions to correctional services',
        'targets': ['Custodial and community admissions'],
        'constraints': {},
    },
    35100015: {
        'name': 'Adult custody admissions to correctional services by sex',
        'targets': ['Custodial admissions', 'Sex'],
        'constraints': {},
    },
    35100016: {
        'name': 'Adult custody admissions to correctional services by aboriginal identity',
        'targets': ['Custodial admissions', 'Aboriginal identity'],
        'constraints': {},
    },
    35100017: {
        'name': 'Adult custody admissions to correctional services by age group',
        'targets': ['Custodial admissions', 'Age group'],
        'constraints': {},
    },
    35100018: {
        'name': 'Adult sentenced custody admissions to correctional services by sex and sentence length ordered',
        'targets': ['Sex', 'Sentence length ordered'],
        'constraints': {},
    },
    35100019: {
        'name': 'Adult admissions to community services by sex',
        'targets': ['Community admissions', 'Sex'],
        'constraints': {},
    },
    35100020: {
        'name': 'Adult admissions to community services by aboriginal identity',
        'targets': ['Community admissions', 'Aboriginal identity'],
        'constraints': {},
    },
    35100021: {
        'name': 'Adult admissions to community services by age group',
        'targets': ['Community admissions', 'Age group'],
        'constraints': {},
    },
    35100022: {
        'name': 'Adult admissions to federal correctional services',
        'targets': ['Custodial and community admissions'],
        'constraints': {},
    },
    35100023: {
        'name': 'Adult probation admissions to community services by aggregate probation length ordered',
        'targets': ['Aggregate probation length ordered'],
        'constraints': {},
    },
    35100024: {
        'name': 'Adult releases from correctional services by sex and aggregate time served',
        'targets': ['Custodial releases', 'Sex', 'Aggregate time served'],
        'constraints': {},
    },
    35100003: {
        'name': 'Average counts of young persons in provincial and territorial correctional services',
        'targets': ['Custodial and community supervision'],
        'constraints': {
            'UOM': 'Persons',
        },
    },
    35100154: {
        'name': 'Average counts of adults in provincial and territorial correctional programs',
        'targets': ['Custodial and community supervision'],
        'constraints': {
            'UOM': 'Persons',
        },
    },
    35100155: {
        'name': 'Average counts of offenders in federal programs, Canada and regions',
        'targets': ['Custodial and community supervision'],
        'constraints': {
            'UOM': 'Persons',
        },
    },
}

RESIDENT_POPULATION_STATCAN_ID = 17100005


class StatCan:
    def __init__(self):
        self._cache = {}

    def get(self, statcan_id):
        if statcan_id not in self._cache:
            url = f'https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{statcan_id}/en'
            response = requests.get(url)
            if not response.ok:
                raise StatCanDownloadError(f"Failed to download information for {statcan_id}\n"
                                           f"Error was {response.text}")

            content = json.loads(response.content)
            zip_url = content['object']
            zip_response = requests.get(zip_url, stream=False)
            if not zip_response.ok:
                raise StatCanDownloadError(f"Failed to download zip file for {statcan_id}\n"
                                           f"Error was {zip_response.text}")

            zip_content = zipfile.ZipFile(io.BytesIO(zip_response.content))
            self._cache[statcan_id] = pd.read_csv(zip_content.open(f'{statcan_id}.csv'), low_memory=False)
        return self._cache[statcan_id]

    def get_resident_pop(self):
        return self.get(RESIDENT_POPULATION_STATCAN_ID)


def main(argv):
    statcan = StatCan()
    joined = pd.DataFrame()
    for statcan_id, config in STATCAN_IDS.items():
        df = statcan.get(statcan_id)
        df = df.set_index(df.REF_DATE + ':' + df.GEO)

        for col, val  in config['constraints'].items():
            df = df.loc[df[col] == val]

        df['target'] = df[config['targets'][0]]
        for next_target in config['targets'][1:]:
            df['target'] = df['target'] + ':' + df[next_target]

        df = df.reset_index().pivot('index', 'target', 'VALUE')
        df.columns = [config['name'] + ':' + c for c in df.columns]

        if joined.empty:
            joined = df
        else:
            joined = joined.join(df)

    joined.to_csv('data/statcan.csv')


if __name__ == "__main__":
    sys.exit(main(sys.argv))
