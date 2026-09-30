# DS 785
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

This repository contains the data sets and code for my DS 785 Capstone project. 

## Install 

## Usage

The contents of this repository contain the data and code necessary to recreate the EV detection model for the capstone project. Scripts for analysis, ETL, and model building are written in either R or Python. Information on what each does and how they should be run is detailed in the [R Files](#r-files) and [Python Files](#python-files) sections.

## Directory Layout

A quick guide to the repository directory layout:

* `raw_data` - this directory contains the raw data directly from the Meter Data Management System (MDMS).
* `labeled_data` - directory containing raw data after labels have been applied to denote if a time period is associated with EV charging
* `Raw Data Analysis.rmd` - R file to examine association between raw primary meter and EV meter data. 

## R Files

There are numerious RMD files for data analysis and data labeling. Starting with data in the `raw_data` folder the following procedure should be used to generate labeled data for EV model building. 

1. `Label Data.rmd` - this file will iterate through the raw data files an annotate if usage values belong to a time period when an EV was actively charging. Annotated files will be stored in the `labeled_data` folder. 

## Contributing

No contributions accepted - this repository will only be visible until the Capstone is completed.

## License

UNLICENSED