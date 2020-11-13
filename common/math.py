def percent_change(df):
    return 100 * (df - df.iloc[0]) / df.iloc[0]
