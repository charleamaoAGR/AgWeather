"""
Created on Fri May 31 9:00:00 2019

@author: CAmao

Purpose: PotatoBlight contains the necessary functions to calculate all station DSVs listed in
'2018 Permanent Stations.xlsx'.

Date modified: Fri May 31 2019
"""

from agweather_package import WeatherStation
from agweather_package import get_path_dir
from agweather_package import download_txt_request
from agweather_package import split_text_file
from datetime import datetime
from tqdm import tqdm
import csv

"""
Purpose: This function downloads mawp15.txt from the mbag website, parses the data it finds and organizes it
by station name.
"""


def initialize_stations():
    # Download mawp15.txt into the input_data folder.
    download_txt_request('https://mbagweather.ca/partners/win/mawp15.txt', 'mawp15.txt')
    # We split the text file by '\n' in order to iterate over each line.
    data = split_text_file('mawp15.txt')
    stations_dict = {}
    # We need station_ids as a set because station ids are always unique.
    station_ids = set()
    # We calculate the size in order to initialize the progress bar.
    size = len(data)

    # Iterate over each line in the text file. We wrape 'data' with tqdm in order to generate a progress bar.
    for each in tqdm(data, desc="Calculating station DSVs", total=size):
        # We generate a list of the data by using ',' as the separator.
        data_list = each.strip('\n').split(',')
        # Station ID is the second data point after the date.
        station_id = data_list[1]

        # Check if station ID, temperature, and RH contain invalid values. If they do, then skip this data point.
        if station_id != '-7999' and data_list[2] != '-7999' and data_list[3] != '-7999':
            # Check if the WeatherStation object has already been created.
            if station_id not in station_ids:
                # If first time encountering the station then add it to the set.
                station_ids.add(station_id)
                # Create new WeatherStation object using the unique station_id.
                new_obj = WeatherStation(station_id)
                # Add the data point to the new object.
                new_obj.add_data(data_list)
                # Add the new WeatherStation into the dictionary for later access.
                stations_dict[station_id] = new_obj
            # If WeatherStation for that station ID has been created then simply add the data to the station's list.
            else:
                # Append the data towards the end of the station's data list.
                stations_dict[station_id].add_data(data_list)
    return stations_dict


"""
Purpose: show_all_stations_dsv takes all WeatherStation objects from initialize_stations and analyzes the daily
data stored within each one. The function calculates cumulative and daily DSV for each WeatherStation
based on a specified seed date of the format YYYY-MM-DD.
"""


def show_all_stations_dsv():
    user_date = raw_input("\nPlease specify a \"seed\" date (YYYY-MM-DD):")
    # Use initialize_stations to get us the dictionary of WeatherStation objects.
    stations = initialize_stations()
    # Create/overwrite the comparison.txt file.
    comparison_file = open(get_path_dir('raw_output_data', 'comparison.txt'), 'w+')
    output_txt = ""
    # Create/overwrite the station_dsv.csv file.
    csv_file = open(get_path_dir('raw_output_data', 'station_dsv.csv'), 'wb')
    csv_obj = csv.writer(csv_file, delimiter=',')
    # Write the headers first.
    csv_obj.writerow(['Station', 'Cumulative DSV', 'Today DSV'])
    # Iterate through each WeatherStation object.
    for each in stations.values():
        # If WeatherStation.invalid_data_flag is True then warn the user.
        if each.invalid_data_flag:
            print "Station %s flagged for invalid data. May have skipped some days for this station." % each.get_id()
        # Calculate the daily dsv and cumulative dsv, and get calculations.
        daily_dsv, cumul_dsv, new_txt = each.today_dsv(datetime.strptime(user_date.strip(), '%Y-%m-%d'))
        # Add the new calculations to the result string.
        output_txt += new_txt
        # Write the dsv values into the station_dsv.csv.
        csv_obj.writerow([each.get_id(), cumul_dsv, daily_dsv])
    # Write the calculations into comparisons.txt
    comparison_file.write(output_txt)
    comparison_file.close()
    csv_file.close()



