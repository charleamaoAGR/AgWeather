from agweather_package import WeatherStation
from agweather_package import get_path_dir
from agweather_package import download_data
from datetime import datetime
import csv


def initialize_stations():
    data = download_data('https://mbagweather.ca/partners/win/mawp15.txt')
    stations_dict = {}
    station_ids = set()

    for each in data:
        data_list = each.strip('\n').split(',')
        station_id = data_list[1]

        if station_id != '-7999' and data_list[2] != '-7999' and data_list[3] != '-7999':
            if station_id not in station_ids:
                station_ids.add(station_id)
                new_obj = WeatherStation(station_id)
                new_obj.add_data(data_list)
                stations_dict[station_id] = new_obj
            else:
                stations_dict[station_id].add_data(data_list)
    return stations_dict


def show_all_stations_dsv():

    stations = initialize_stations()
    comparison_file = open(get_path_dir('raw_output_data', 'comparison.txt'), 'w+')
    output_txt = ""
    for each in stations.values():
        if each.invalid_data_flag:
            print "Station %s flagged for invalid data. May have skipped some days for this station." % each.get_id()
        daily_dsv, cumul_dsv, new_txt = each.today_dsv(datetime.strptime("2019-05-02", '%Y-%m-%d'))
        output_txt += new_txt
        print "Station - %s | Cumulative DSV - %s | Today DSV - %s" % (each.get_id(), cumul_dsv, daily_dsv)
    comparison_file.write(output_txt)
    comparison_file.close()



