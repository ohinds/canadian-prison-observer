import os
import sys

import matplotlib.pylab as plt
import pandas as pd

from common.plot import save_plot
from ingest.statcan import StatCan


START_YEAR = 1979


def load_statcan():
    df = pd.read_csv(os.path.join('data', 'statcan.csv'))
    return df.loc[df.Year >= START_YEAR]


def compute_resident_pop():
    res_pop = StatCan().get_resident_pop()
    res_pop = res_pop.loc[
        (res_pop['Sex'] == 'Both sexes') &
        (res_pop['Age group'] == 'All ages') &
        (res_pop['GEO'] == 'Canada')
    ]
    res_pop['Year'] = res_pop['REF_DATE']
    res_pop['Geo'] = res_pop['GEO'].str.upper()

    return res_pop.groupby('Year').VALUE.sum()


def national(statcan):
    country = statcan.loc[
        ((statcan['Geo Type'] == 'COUNTRY') & (statcan['Geo'] == 'CANADA')) |
        (statcan['Geo Type'] == 'PROVINCE')
    ]

    def interp_and_sum(df):
        fed_count_col = 'Average counts of offenders in federal programs, Canada and regions:Actual-in count'
        fed_count = df.pivot('Year', 'Geo', fed_count_col).interpolate().sum(axis=1)

        prov_count_col = 'Average counts of adults in provincial and territorial correctional programs:Total actual-in count'
        prov_count = df.pivot('Year', 'Geo', prov_count_col).interpolate().sum(axis=1)

        youth_count_col = 'Average counts of young persons in provincial and territorial correctional services:Total actual-in count'
        youth_count = df.pivot('Year', 'Geo', youth_count_col).interpolate().sum(axis=1)

        return fed_count + prov_count + youth_count

    def percent_change(df):
        return 100 * (df - df.iloc[0]) / df.iloc[0]

    count = interp_and_sum(country)
    plt.plot(count)
    save_plot("Average National Number of Incarcerated People")
    count.name = "Number of Incarcerated People"

    count_ptc = percent_change(count)
    plt.plot(count_ptc)
    save_plot("% Change in Average National Number of Incarcerated People")

    res_pop = compute_resident_pop()

    plt.plot(res_pop)
    save_plot("National Resident Population")

    plt.plot(percent_change(res_pop))
    save_plot("% Change in National Resident Population")

    rate = 100000 * (count / res_pop).dropna()
    plt.plot(rate)
    save_plot("Average National Number of Incarcerated People Per 100,000 Residents")
    print(f"Average National Number of Incarcerated People Per 100,000 Residents:\n{rate}")
    rate.name = "Number of Incarcerated People per 100,000 Residents"

    plt.plot(percent_change(rate))
    save_plot("% Change in Average National Number of Incarcerated People Per 100,000 Residents")

    pd.concat([count, rate], axis=1).to_csv(os.path.join(os.path.dirname(__file__), 'national.csv'), float_format="%0.0f")


def main(argv):
    plt.rcParams["figure.figsize"] = [6.5, 3.64]
    plt.rcParams["figure.dpi"] = 90

    statcan = load_statcan()
    national(statcan)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
