import io
import json
import requests
import sys
import zipfile

import pandas as pd


class StatCanDownloadError(Exception):
    pass


STATCAN_IDS = {
    35100013: 'Operating expenditures for adult correctional services',
    35100014: 'Adult admissions to correctional services',
    35100015: 'Adult custody admissions to correctional services by sex',
    35100016: 'Adult custody admissions to correctional services by aboriginal identity',
    35100017: 'Adult custody admissions to correctional services by age group',
    35100018: 'Adult sentenced custody admissions to correctional services by sex and sentence length ordered',
    35100019: 'Adult admissions to community services by sex',
    35100020: 'Adult admissions to community services by aboriginal identity',
    35100021: 'Adult admissions to community services by age group',
    35100022: 'Adult admissions to federal correctional services',
    35100023: 'Adult probation admissions to community services by aggregate probation length ordered',
    35100024: 'Adult releases from correctional services by sex and aggregate time served',
    35100003: 'Average counts of young persons in provincial and territorial correctional services',
    35100154: 'Average counts of adults in provincial and territorial correctional programs',
    35100155: 'Average counts of offenders in federal programs, Canada and regions',
}


def get_table(statcan_id):
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
    return pd.read_csv(zip_content.open(f'{statcan_id}.csv'))


def main(argv):
    tables = {}
    for statcan_id, name in STATCAN_IDS.items():
        tables[statcan_id] = get_table(statcan_id)
        tables[statcan_id].to_csv(f'{statcan_id}.csv')

    breakpoint()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
