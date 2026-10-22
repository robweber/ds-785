"""fix_dates.py
Given the path to a directory that contains files already downloaded from the MDM system
this will attempt to read each CSV and fix the UTC timestamps by converting them back
to the local time.

The CSV files `start-date-time` and `end-date-time` for each interval will be removed
and replaced with `start_date`, `start_time`, `end_date` and `end_time`.

A few other columns are renamed or removed as they provide no value.

Example:

python3 fix_dates.py

"""
import argparse
import csv
import os
import os.path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FIELDS = ["meter_num", "value", "vee-value", "unit-of-measure",
          "channel", "start_full", "start_date", "start_time", "end_full", "end_date", "end_time"]

CENTRAL = ZoneInfo("America/Chicago")

def fix_date(utc_date):
    """Convert a UTC timestamp string to local (Central) time."""
    utc_dt = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%S.000%z")
    return utc_dt.astimezone(CENTRAL)


def update_csv(file):
    """corrects the start and end time for a single CSV file """
    print(f"Correcting {file}")

    # open the csv file
    updated_values = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:

            # fix each the start and end date
            for t in ('start', 'end'):
                new_timestamp = fix_date(row[f"{t}-date-time"])

                row[f"{t}_date"] = new_timestamp.strftime("%m-%d-%Y")
                row[f"{t}_time"] = new_timestamp.strftime("%H:%M")
                row[f"{t}_full"] = new_timestamp.strftime("%m-%d-%Y %H:%M")

                # delete the old values
                row.pop(f"{t}-date-time")

            # also fix a few other column names
            row["meter_num"] = row['asset-id']

            # remove ones we don't need
            row.pop("source-domain")
            row.pop("asset-type")
            row.pop("asset-id")
            row.pop("flow-direction")

            updated_values.append(row)

    # write a new csv
    new_file = os.path.join(os.path.dirname(file), f"{os.path.basename(file)[:-4]}.corrected.csv")
    with open(new_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)

        writer.writeheader()
        for reading in updated_values:
            writer.writerow(reading)


def main():
    """Main method, run when script is executed"""
    # setup the command line parser
    parser = argparse.ArgumentParser(description="Corrects the date in CSV files downloaded by the NISC Downloader (UTC back to local time)")
    parser.add_argument('-d', '--directory', required=False, type=str, default="reading_downloads",
                        help="The directory containing the csv files to update")

    args = parser.parse_args()

    # parse the directory of CSV files
    for file in os.listdir(args.directory):
        # make sure it's a csv but not an already corrected one
        if(file.endswith('.csv') and not file.endswith('.corrected.csv')):
            update_csv(os.path.join(args.directory, file))


if __name__ == '__main__':
    main()
