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

def generate_features(file):
    # open the file
    df = pd.read_csv(file)

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
            df = generate_features(f"{root}/{f}")

            # save the new dataframe in the output folder
            df.to_csv(f"{args.output}/{f}", index=False)

if __name__ == '__main__':
    main()
