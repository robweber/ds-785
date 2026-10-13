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
    # previous interval stats
    df['previous_value'] = df['value'].shift(1)
    df['previous_delta'] = df['value'] - df['value'].shift(1)

    # previous averages
    df['previous_hour_mean'] = df['value'].shift(1).rolling(window=4).mean()
    df['previous_day_mean'] = df['value'].shift(1).rolling(window=96).mean()

    # previous std
    df['previous_hour_std'] = df['value'].shift(1).rolling(window=4).std()
    df['previous_day_std'] = df['value'].shift(1).rolling(window=96).std()

    return df

def main():
    """Main method, run when script is executed"""

    # setup the command line parser
    parser = argparse.ArgumentParser(description="Generates features from labeled data")
    parser.add_argument('-i', '--input', required=False, type=str, default="labeled_data",
                        help="The directory containing the labeled data to add features")
    parser.add_argument("-o", "--output", required=False, type=str, default="model_data",
                        help="The directory to output the modified files")

    args = parser.parse_args()

    # recursively walk the diretory
    for root, dirs, files in os.walk(args.input):
        for f in files:
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
            else:
                print(f"ERROR: Cannot generate features for {f}")

if __name__ == '__main__':
    main()
