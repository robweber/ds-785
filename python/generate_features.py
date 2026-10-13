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

def clean_outliers(df):
    """ replaces outliers with reasonable estimates based on previous intervals """

    # get all columns over threshold
    outliers = df['value'] > MAX_INTERVAL_THRESHOLD

    # replace outliers with NA https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.mask.html
    no_outliers = df['value'].mask(outliers)

    # interpolate NA values based on surrounding values - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html#pandas.DataFrame.interpolate
    df["kwh_imputed"] = no_outliers.interpolate(method="linear", limit_area="inside")

    if(outliers.sum() > 0):
        print(f"\t{outliers.sum()} outliers found")

    return df


def generate_features(df):

    # previous interval
    df['previous_value'] = df['value'].shift(1)

    # avg usage previous hour (4 intervals)
    df['previous_hour_mean'] = df['value'].rolling(window=4).mean().shift(1)

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
            # for each file, generate the features
            print(f"Generating features for {f}")

            # read in the file as a dataframe
            df = pd.read_csv(f"{root}/{f}")

            # fix an outlier data - generally these are from MDM fixes
            df = clean_outliers(df)

            #df = generate_features(df)

            # save the new dataframe in the output folder
            df.to_csv(f"{args.output}/{f}", index=False)

if __name__ == '__main__':
    main()
