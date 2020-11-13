import os
import sys

import matplotlib.pylab as plt
import pandas as pd

from common.geo import FEDERAL_REGION_MAP
from common.math import percent_change
from common.plot import save_plot

from ingest.statcan import StatCan


START_YEAR = 2004


def load_statcan():
    df = pd.read_csv(os.path.join('data', 'statcan.csv'))
    return df.loc[df.Year >= START_YEAR]


def prairies_and_national(statcan):
    country = statcan.loc[
        ((statcan['Geo Type'] == 'COUNTRY') & (statcan['Geo'] == 'CANADA')) |
        (statcan['Geo Type'] == 'PROVINCE')
    ]

    prairies = statcan.loc[
        ((statcan['Geo Type'] == 'REGION') & (statcan['Geo'] == 'PRAIRIE REGION')) |
        ((statcan['Geo Type'] == 'PROVINCE') & (statcan['Geo'].isin(FEDERAL_REGION_MAP['PRAIRIE REGION'])))
    ]

    not_prairies = statcan.loc[
        ((statcan['Geo Type'] == 'REGION') & (statcan['Geo'] != 'PRAIRIE REGION')) |
        ((statcan['Geo Type'] == 'PROVINCE') & ~(statcan['Geo'].isin(FEDERAL_REGION_MAP['PRAIRIE REGION'])))
    ]

    def interp_and_sum(df):
        prov_count_col = 'Adult custody admissions to correctional services by sex:Total, custodial admissions:Female'
        prov_count = df.pivot('Year', 'Geo', prov_count_col).interpolate().sum(axis=1)

        youth_count_col = 'Youth admissions to correctional services by age and sex:Total correctional services:Total, admissions by age:Females'
        youth_count = df.pivot('Year', 'Geo', youth_count_col).interpolate().sum(axis=1)

        return prov_count + youth_count

    def prair_plot(prair, not_prair, title):
        plt.plot(prair, label="Prairies")
        plt.plot(not_prair, label="The Rest of Canada")
        plt.legend(frameon=False)
        save_plot(title)

    count = interp_and_sum(country)
    print(count)
    print(percent_change(count))

    prairies_count = interp_and_sum(prairies)
    not_prairies_count = interp_and_sum(not_prairies)
    prair_plot(prairies_count, not_prairies_count, "Women's Carceral Admissions")

    print(percent_change(prairies_count))
    print(percent_change(not_prairies_count))

    prairies_count.name = "Prairies"
    not_prairies_count.name = "The Rest of the Country"
    pd.concat([prairies_count, not_prairies_count], axis=1).to_csv(os.path.join(os.path.dirname(__file__), 'admissions.csv'))


def main(argv):
    plt.rcParams["figure.figsize"] = [6.5, 3.64]
    plt.rcParams["figure.dpi"] = 90

    statcan = load_statcan()
    prairies_and_national(statcan)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
