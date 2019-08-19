import yaml
from .UsefulFunctions import get_path_dir
from .UsefulClasses import GroupedArray
from datetime import datetime

DAYS_BEFORE = 7
HOURS_BEFORE = 24*DAYS_BEFORE
STATION_ID_INDEX = 2
TEMP_DATA_INDEX = 3  # Placeholder
PRECIP_DATA_INDEX = 3  # Placeholder
SECONDS_IN_HOUR = 3600


# Export FHB risk calculations for each station to a CSV.
def show_all_fhb_risks():
    pass


# Return GroupedArray of each station with hourly data for the last 7 days.
def extract_7_day_data(valid_date, mawp_60_stream):
    grouped_station_data_array = init_station_grouped_array()
    for each_line in mawp_60_stream:
        time_str = each_line.split(',', 1)[0].strip('"')
        mawp_60_date = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        if check_within_date_range(valid_date, mawp_60_date, HOURS_BEFORE):
            raw_data_line = each_line.split(',')
            temp = raw_data_line[TEMP_DATA_INDEX]
            precip = raw_data_line[PRECIP_DATA_INDEX]
            grouped_station_data_array.insert_data(raw_data_line[STATION_ID_INDEX], [time_str, temp, precip])
    return grouped_station_data_array


# Checks if a date is within the acceptable date range.
def check_within_date_range(latest_ref_datetime, datetime_to_compare, comparison_period_in_hours):
    time_difference_hours = (latest_ref_datetime - datetime_to_compare).total_seconds() / SECONDS_IN_HOUR
    return 0 < time_difference_hours <= comparison_period_in_hours


# Returns a GroupedArray containing an empty dictionary with the station_id's as the dictionary keys.
def init_station_grouped_array():
    station_array = GroupedArray()
    with open(get_path_dir('config_files', 'mbag_stations.yaml'), 'r') as mbag_yaml:
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



