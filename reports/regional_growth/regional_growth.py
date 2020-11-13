import os
import sys

import matplotlib.pylab as plt
import pandas as pd

from common.geo import FEDERAL_REGION_MAP
from common.plot import save_plot
from ingest.globe_and_mail import GlobeAndMail
from ingest.statcan import StatCan


START_YEAR = 2004


def load_statcan():
    df = pd.read_csv(os.path.join('data', 'statcan.csv'))
    return df.loc[df.Year >= START_YEAR]


def load_globe():
    df = GlobeAndMail().get()
    df = df.loc[df['IN CUSTODY/COMMUNITY'] == 'In Custody']
    df['YEAR'] = ('20' + df['FISCAL YEAR'].str[-2:]).astype(int)
    return df.loc[df.YEAR >= START_YEAR].groupby(['YEAR', 'OFFENDER NUMBER']).first().reset_index()


def compute_resident_pop():
    res_pop = StatCan().get_resident_pop()
    res_pop = res_pop.loc[
        (res_pop['Sex'] == 'Both sexes') &
        (res_pop['Age group'] == 'All ages') &
        (res_pop['GEO'] != 'Canada')
    ]
    res_pop['Year'] = res_pop['REF_DATE']
    res_pop['Geo'] = res_pop['GEO'].str.upper()

    return (
        res_pop.loc[res_pop.Geo.isin(FEDERAL_REGION_MAP['PRAIRIE REGION'])].groupby('Year').VALUE.sum(),
        res_pop.loc[~res_pop.Geo.isin(FEDERAL_REGION_MAP['PRAIRIE REGION'])].groupby('Year').VALUE.sum(),
    )


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
        fed_count_col = 'Average counts of offenders in federal programs, Canada and regions:Actual-in count'
        fed_count = df.pivot('Year', 'Geo', fed_count_col).interpolate().sum(axis=1)

        prov_count_col = 'Average counts of adults in provincial and territorial correctional programs:Total actual-in count'
        prov_count = df.pivot('Year', 'Geo', prov_count_col).interpolate().sum(axis=1)

        youth_count_col = 'Average counts of young persons in provincial and territorial correctional services:Total actual-in count'
        youth_count = df.pivot('Year', 'Geo', youth_count_col).interpolate().sum(axis=1)

        return fed_count + prov_count + youth_count

    def percent_change(df):
        return 100 * (df - df.iloc[0]) / df.iloc[0]

    def prair_plot(prair, not_prair, title):
        plt.plot(prair, label="Prairies")
        plt.plot(not_prair, label="The Rest of Canada")
        plt.legend(frameon=False)
        save_plot(title)

    count = interp_and_sum(country)
    plt.plot(count)
    save_plot("Average National Number of Incarcerated People")

    prairies_count = interp_and_sum(prairies)
    not_prairies_count = interp_and_sum(not_prairies)
    prair_plot(prairies_count, not_prairies_count, "Average Number of Incarcerated People")

    count_ptc = percent_change(count)
    plt.plot(count_ptc)
    save_plot("% Change in Average National Number of Incarcerated People")

    prairies_count_ptc = percent_change(prairies_count)
    not_prairies_count_ptc = percent_change(not_prairies_count)
    prair_plot(prairies_count_ptc, not_prairies_count_ptc, "% Change in Average Number of Incarcerated People")

    prairies_res_pop, not_prairies_res_pop = compute_resident_pop()
    res_pop = prairies_res_pop + not_prairies_res_pop

    plt.plot(res_pop)
    save_plot("National Resident Population")
    prair_plot(prairies_res_pop, not_prairies_res_pop, "Resident Population")

    plt.plot(percent_change(res_pop))
    save_plot("% Change in National Resident Population")

    prairies_res_pop_ptc = percent_change(prairies_res_pop)
    not_prairies_res_pop_ptc = percent_change(not_prairies_res_pop)
    prair_plot(prairies_res_pop_ptc, not_prairies_res_pop_ptc, "% Change in Resident Population")

    rate = 100000 * (count / res_pop).dropna()
    plt.plot(rate)
    save_plot("Average National Number of Incarcerated People Per 100,000 Residents")
    print(f"Average National Number of Incarcerated People Per 100,000 Residents:\n{rate}")

    prairies_rate = 100000 * (prairies_count / prairies_res_pop).dropna()
    not_prairies_rate = 100000 * (not_prairies_count / not_prairies_res_pop).dropna()
    prair_plot(prairies_rate, not_prairies_rate, "Average Number of Incarcerated People Per 100,000 Residents")

    plt.plot(percent_change(rate))
    save_plot("% Change in Average National Number of Incarcerated People Per 100,000 Residents")

    prairies_rate_ptc = percent_change(prairies_rate)
    not_prairies_rate_ptc = percent_change(not_prairies_rate)
    prair_plot(prairies_rate_ptc, not_prairies_rate_ptc, "% Change in Average Number of Incarcerated People Per 100,000 Residents")

    prairies_rate_ptc.name = "Prairies"
    not_prairies_rate_ptc.name = "The Rest of the Country"
    pd.concat([prairies_rate_ptc, not_prairies_rate_ptc], axis=1).to_csv(os.path.join(os.path.dirname(__file__), 'ptc_change_ave_inc_rate.csv'), float_format="%0.2f")


def ind_gender(globe):
    globe['PRAIRIE REGION'] = globe['PROVINCE'].isin(FEDERAL_REGION_MAP['PRAIRIE REGION'])
    nat = globe.groupby('YEAR')['OFFENDER NUMBER'].count()
    gender = globe.groupby(['YEAR', 'GENDER'])['OFFENDER NUMBER'].count()
    race_group = globe.groupby(['YEAR', 'RACE GROUPING'])['OFFENDER NUMBER'].count()
    region_gender_race_group = globe.groupby(['YEAR', 'PRAIRIE REGION', 'GENDER', 'RACE GROUPING'])['OFFENDER NUMBER'].count()
    breakpoint()


def main(argv):
    plt.rcParams["figure.figsize"] = [6.5, 3.64]
    plt.rcParams["figure.dpi"] = 90

    statcan = load_statcan()
    prairies_and_national(statcan)

    # globe = load_globe()
    # ind_gender(globe)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
