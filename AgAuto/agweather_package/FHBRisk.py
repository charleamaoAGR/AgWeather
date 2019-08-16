import yaml
from .UsefulFunctions import get_path_dir
from .UsefulClasses import GroupedArray
from datetime import datetime

DAYS_BEFORE = 7
HOURS_BEFORE = 24*DAYS_BEFORE


# Export FHB risk calculations for each station to a CSV.
def show_all_fhb_risks():
    pass


# Return GroupedArray of each station with hourly data for the last 7 days.
def extract_7_day_data(valid_date, mawp_60_stream):
    grouped_station_data_array = init_station_grouped_array()
    for each_line in mawp_60_stream:
        date_str = each_line.split(',', 1)[0]
        mawp_60_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        if check_within_date_range(valid_date, mawp_60_date, HOURS_BEFORE):
            grouped_station_data_array.insert_data()
    pass


# Checks if a date is within the acceptable date range.
def check_within_date_range(latest_ref_datetime, datetime_to_compare, comparison_period_in_hours):
    time_difference_hours = (latest_ref_datetime - datetime_to_compare).total_seconds() / 3600
    return 0 < time_difference_hours < comparison_period_in_hours


# Returns a GroupedArray containing an empty dictionary with the station_id's as the dictionary keys.
def init_station_grouped_array():
    station_array = GroupedArray()
    with open(get_path_dir('input_data', 'mbag_stations.yaml'), 'r') as mbag_yaml:
        station_yaml_info = yaml.safe_load(mbag_yaml)
        for each_station in station_yaml_info:
            station_array.add_identifier(each_station)
    return station_array


# Loops through 7 day hourly data for one station and returns the FHB_V1 Index.
def calc_fhb_index(data_list):
    pass


# Returns a text displaying the FHB_V1 Risk based on a given FHB_V1 Index.
def display_fhb_risk(fhb_index):
    pass



