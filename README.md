# DS 785
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

This repository contains the data sets and code for my DS 785 Capstone project. 

## Install 

## Usage

The contents of this repository contain the data and code necessary to recreate the EV detection model for the capstone project. Scripts for analysis, ETL, and model building are written in either R or Python. They should be run in a specific order on the raw data files to re-create the model. 

### Prep Raw Data

__Note:__ this does not need to be done on files in this repo, these files have already been modified from MDM. 

1. On data downloaded directly from the MDM system, run the Python script `python/fix_dates.py -d {path_to_dir}`.

### Label Data

__Note:__ this does not need to be done on files in this repo. These files have already been labeled. 

Data must be merged and labeled to train the model. This process will merge the EV charger data with the primary meter data, adding the EV boolean attribute. It will also add temperature data from the weather file to each date. During labeling the correct number of intervals will be verified to ensure a complete dataset. 

1. Open the `Label Data.Rmd` file. Note the packages that must be available. 
2. Change the `MERGE_EV` variable at the top depending on what dataset you are working with (EV or Non-EV data)
3. Run the subsequent cells to label the data
4. Note the output of the last cell. Any `FALSE` values indicate a file that did not pass validation. 

Re-run this process for both the EV and non-EV account data to generate the labeled data.

## Directory Layout

A quick guide to the repository directory layout:

* `raw_data` - this directory contains the raw data weather and meter data. Meter data is directly from the Meter Data Management System (MDMS).
* `labeled_data` - directory containing raw data after labels have been applied to denote if a time period is associated with EV charging, some basic cleaning also done
* `python` - Python scripts
* `Label Data.Rmd` - R file to label the raw data for model building. This will merge the EV data with the primary meter data. 
* `Raw Data Analysis.Rmd` - R file to examine association between raw primary meter and EV meter data. 

## Contributing

No contributions accepted - this repository will only be visible until the Capstone is completed.

## License

UNLICENSED