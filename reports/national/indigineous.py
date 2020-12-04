import os
import sys

import matplotlib.pylab as plt
import pandas as pd

from common.plot import save_plot


INTERP_YEAR = 2001
START_YEAR = 2006


def load_statcan():
    df = pd.read_csv(os.path.join('data', 'statcan.csv'))
    return df.loc[df.Year >= INTERP_YEAR]


def national(statcan):
    country = statcan.loc[
        ((statcan['Geo Type'] == 'COUNTRY') & (statcan['Geo'] == 'CANADA')) |
        (statcan['Geo Type'] == 'PROVINCE')
    ]

    def interp_and_sum(df, indigenous):
        prov_count_col = f'Adult custody admissions to correctional services by aboriginal identity:Total, custodial admissions:{indigenous}'
        prov_count = df.pivot('Year', 'Geo', prov_count_col).interpolate().sum(axis=1)

        youth_indigenous = indigenous[0] + indigenous[1:].lower()
        youth_count_col = f'Youth admissions to correctional services by Aboriginal identity and sex:Total correctional services:{youth_indigenous}:Total, admissions by sex'
        youth_count = df.pivot('Year', 'Geo', youth_count_col).interpolate().sum(axis=1)

        tot = prov_count + youth_count
        return tot.loc[tot.index >= START_YEAR]

    def percent_change(df):
        return 100 * (df - df.iloc[0]) / df.iloc[0]

    ind_count = interp_and_sum(country, 'Aboriginal identity')
    plt.plot(ind_count)
    save_plot("Indigenous Admissions to Incarceration")
    ind_count.name = "Indigenous Admissions to Incarceration"

    non_ind_count = interp_and_sum(country, 'Non-Aboriginal identity')
    plt.plot(non_ind_count)
    save_plot("Non-indigenous Admissions to Incarceration")
    non_ind_count.name = "Non-indigenous Admissions to Incarceration"

    ind_count_ptc = percent_change(ind_count)
    plt.plot(ind_count_ptc)
    save_plot("% Change in Indigenous Admissions to Incarceration")

    non_ind_count_ptc = percent_change(non_ind_count)
    plt.plot(non_ind_count_ptc)
    save_plot("% Change in Non-indigenous Admissions to Incarceration")

    pd.concat([ind_count, ind_count_ptc, non_ind_count, non_ind_count_ptc], axis=1).to_csv(os.path.join(os.path.dirname(__file__), 'indigenous_adm.csv'), float_format="%0.0f")


def main(argv):
    plt.rcParams["figure.figsize"] = [6.5, 3.64]
    plt.rcParams["figure.dpi"] = 90

    statcan = load_statcan()
    national(statcan)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
