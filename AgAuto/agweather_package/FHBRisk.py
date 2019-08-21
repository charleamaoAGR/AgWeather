import yaml
from .UsefulFunctions import get_path_dir
from .UsefulClasses import GroupedArray
from datetime import datetime
from tabulate import tabulate

DAYS_BEFORE = 7
HOURS_BEFORE = 24*DAYS_BEFORE
STATION_ID_INDEX = 2
SECONDS_IN_HOUR = 3600
AVG_AIR_T_INDEX = 5  # Look at MAWP-Data-Table-Def.xlsx
PLUVIO_RAIN_INDEX = 10


# Export FHB risk calculations for each station to a CSV.
def show_all_fhb_risks():
    station_desc_dict = init_station_desc_dict()
    table_contents = [['STATION_ID', 'STATION', 'FHB_DT', 'DPPT7', 'T15307', 'FHB_V1_Index', 'FHB_V1_Risk']]
    with open('mawp60raw.txt', 'r') as mawp_60_file:
        date_input = input("Input FHB reference date in format YYYY-mm-dd hh:MM: ")
        weather_data = extract_7_day_data(datetime.strptime(date_input.strip(), '%Y-%m-%d %H:%M'), mawp_60_file)

    for each_station in weather_data.get_identifiers():
        if len(weather_data.get_data(each_station)) != 0:
            dppt7, t15307, fhb_index = calc_fhb_index(weather_data.get_data(each_station))
            # Note if you get KeyErrors below, then review mbag_stations.yaml if it needs to be updated.
            table_contents.append([each_station, station_desc_dict[each_station], date_input, dppt7, t15307,
                                   '%.2f' % fhb_index, display_fhb_risk(fhb_index)])

    print(tabulate(table_contents))

    return table_contents


# Return GroupedArray of each station with hourly data for the last 7 days.
def extract_7_day_data(valid_date, mawp_60_stream):
    grouped_station_data_array = init_station_grouped_array()
    for each_line in mawp_60_stream:
        time_str = each_line.split(',', 1)[0].strip('"')
        mawp_60_date = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        if check_within_date_range(valid_date, mawp_60_date, HOURS_BEFORE):
            raw_data_line = each_line.split(',')
            temp = raw_data_line[AVG_AIR_T_INDEX]
            precip = raw_data_line[PLUVIO_RAIN_INDEX]
            grouped_station_data_array.insert_data(int(raw_data_line[STATION_ID_INDEX]), [time_str, temp, precip])
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


# Returns a dictionary with the station ID's as keys and the station descriptions as values.
def init_station_desc_dict():
    station_dict = {}
    with open(get_path_dir('config_files', 'mbag_stations.yaml'), 'r') as mbag_yaml:
        station_yaml_info = yaml.safe_load(mbag_yaml)
        for each_station in station_yaml_info:
            station_dict[each_station] = station_yaml_info[each_station]['desc']
    return station_dict


# Loops through 7 day hourly data for one station and returns the FHB_V1 Index.
def calc_fhb_index(data_list, temp_index=1, precip_index=2):
    t15307 = 0
    dppt7 = 0
    for each_data in data_list:
        if each_data[temp_index] != '' or each_data[precip_index] != '':  # Data needs to be cleaned by mawpcleaner.
            if 15 <= float(each_data[temp_index]) <= 30:
                t15307 += 1
            if float(each_data[precip_index]) > 0:
                dppt7 += 1
    return dppt7, t15307, (dppt7/39.0*t15307/168.0)*100


# Returns a text displaying the FHB_V1 Risk based on a given FHB_V1 Index.
def display_fhb_risk(fhb_index):
    risk_display = ""
    if fhb_index < 12:
        risk_display = "low"
    elif 12 <= fhb_index < 22:
        risk_display = "moderate"
    elif 22 <= fhb_index <= 32:
        risk_display = "high"
    elif fhb_index > 32:
        risk_display = "extreme"
    return risk_display
