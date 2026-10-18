"""generate_features.py

Generates machine learning features from a directory of meter data (values and dates).
Updated CSV files are exported to the output directory.

Adapted some code examples from: https://machinelearningmastery.com/7-pandas-tricks-for-time-series-feature-engineering/

Features generated:

* Previous interval - value from previous record
* Previous hour mean - mean value from 4 previous intervals (1 hr)

"""

import argparse
import os
import pandas as pd

MAX_INTERVAL_THRESHOLD = 12  # 12 kWh is max 200 amp meter could use in 15 min
HOUR_INTERVAL = 4  # number of intervals in an hour
DAILY_INTERVAL = HOUR_INTERVAL * 24  # number of intervals in a full day

def is_data_valid(df):
    """ basic checks on the data to ensure correct number of intervals and values """

    # check for NA values - R code should have already verified other attributes
    return df['value'].isna().sum() == 0

def clean_outliers(df):
    """ replaces outliers with reasonable estimates based on previous intervals """

    # get all columns over threshold
    outliers = df['value'] > MAX_INTERVAL_THRESHOLD

    # replace outliers with NA https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.mask.html
    no_outliers = df['value'].mask(outliers)

    # interpolate NA values based on surrounding values - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html#pandas.DataFrame.interpolate
    df["value"] = no_outliers.interpolate(method="linear", limit_area="inside")

    if(outliers.sum() > 0):
        print(f"\t{outliers.sum()} outliers found")

    return df


def generate_features(df):

    # VALUE features
    # baseline usage over 30 days (forward and reverse)
    df['30_day_kwh_baseline'] = df['value'].rolling(window=DAILY_INTERVAL * 30, center=True, min_periods=1).median()

    # previous interval stats
    df['previous_value'] = df['value'].shift(1)
    df['previous_value_delta'] = df['value'] - df['value'].shift(1)
    df['baseline_value_delta'] = df['value'] - df['30_day_kwh_baseline']

    # previous averages
    df['previous_hour_value_mean'] = df['value'].shift(1).rolling(window=HOUR_INTERVAL).mean()
    df['previous_day_value_mean'] = df['value'].shift(1).rolling(window=DAILY_INTERVAL).mean()

    # previous std
    df['previous_hour_value_std'] = df['value'].shift(1).rolling(window=HOUR_INTERVAL).std()
    df['previous_day_value_std'] = df['value'].shift(1).rolling(window=DAILY_INTERVAL).std()

    # WEATHER features
    # change from mean of previous 4 values - indication of climbing or falling
    df['previous_hour_temperature_delta'] = df['temperature'] - df['temperature'].shift(1).rolling(window=HOUR_INTERVAL).mean()

    # rolling averages to establish baseline temp
    df['daily_temperature_mean'] = df['temperature'].rolling(window=DAILY_INTERVAL, center=True, min_periods=1).median()
    df['weekly_temperature_mean'] = df['temperature'].rolling(window=DAILY_INTERVAL * 7, center=True, min_periods=1).median()

    # add delta from weekly baseline
    df['baseline_temperature_delta'] = df['temperature'] - df['weekly_temperature_mean']

    # TIME features - help from https://www.geeksforgeeks.org/pandas/get-month-from-date-in-pandas-python/
    start_dates = pd.to_datetime(df['start_date'])
    df['month'] = start_dates.dt.month
    df['day_of_week'] = start_dates.dt.weekday
    df['is_weekend'] = start_dates.dt.weekday >= 5  # 5 = Sat, 6 = Sun

    return df

def main():
    """Main method, run when script is executed"""

    # setup the command line parser
    parser = argparse.ArgumentParser(description="Generates features from labeled data")
    parser.add_argument('-i', '--input', required=False, type=str, default="labeled_data",
                        help="The directory containing the labeled data to add features")
    parser.add_argument("-o", "--output", required=False, type=str, default="model_data",
                        help="The directory to output the modified files")
    parser.add_argument('-T', '--test', required=False, action='store_true',
                        help="Running in test processes only one file")

    args = parser.parse_args()

    if(args.test):
        print("Running in TEST MODE - only processing one file")

    # recursively walk the diretory
    keep_running = True
    for root, dirs, files in os.walk(args.input):
        for f in files:
            if(keep_running):
                # read in the file as a dataframe
                df = pd.read_csv(f"{root}/{f}")

                if(is_data_valid(df)):
                    # for each file, generate the features
                    print(f"Generating features for {f}")

                    # fix an outlier data - generally these are from MDM fixes
                    df = clean_outliers(df)

                    df = generate_features(df)

                    # save the new dataframe in the output folder
                    df.to_csv(f"{args.output}/{f}", index=False)

                    keep_running = not args.test  # FALSE if args.test is TRUE
                else:
                    print(f"ERROR: Cannot generate features for {f}")

if __name__ == '__main__':
    main()
