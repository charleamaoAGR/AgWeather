import urllib2
from UsefulClasses import WeatherStation
from datetime import datetime

def download_data(url):

    response = urllib2.urlopen(url)
    data = response.read().split('\n')[1:-1]

    return data


def initialize_stations():
    data = download_data('https://mbagweather.ca/partners/win/mawp15.txt')
    stations_dict = {}
    station_ids = set()

    for each in data:
        data_list = each.strip('\n').split(',')
        station_id = data_list[1]

        if station_id not in station_ids:
            station_ids.add(station_id)
            new_obj = WeatherStation(station_id)
            new_obj.add_data(data_list)
            stations_dict[station_id] = new_obj
        else:
            stations_dict[station_id].add_data(data_list)

    return stations_dict


def main():

    stations = initialize_stations()

    for each in stations.values():
        print "Station - %s | Risk - %s" % (each.get_id(), each.today_cumulative_dsv(datetime.strptime("2019-05-01", '%Y-%m-%d')))

main()
