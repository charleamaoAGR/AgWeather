import urllib2


class WeatherStation:


    data_size = 0

    def __init__(self, station_id):
        self.id = station_id
        self.data = [["DateTime", "StnID", "Temp", "RH", "Rain", "AvgWS", "AvgWD"]]


def download_data(url):

    response = urllib2.urlopen(url)
    data = response.read()

    return data


def wisdom_dsv_lookup(period_count, avg_temperature):

    dsv = -1
    if 0 <= period_count < 39:
        dsv = 0
    elif (39 <= period_count <= 50) and (avg_temperature < 15.5):
        dsv = 0
    elif (39 <= period_count <= 50) and (avg_temperature >= 15.5):
        dsv = 1
    elif (51 <= period_count <= 62) and (avg_temperature < 12.5):
        dsv = 0
    elif (51 <= period_count <= 62) and (12.5 <= avg_temperature < 15.5):
        dsv = 1
    elif (51 <= period_count <= 62) and (avg_temperature >= 15.5):
        dsv = 2
    elif (63 <= period_count <= 74) and (avg_temperature < 12.5):
        dsv = 1
    elif (63 <= period_count <= 74) and (12.5 <= avg_temperature < 15.5):
        dsv = 2
    elif (63 <= period_count <= 74) and (avg_temperature >= 15.5):
        dsv = 3
    elif (75 <= period_count <= 86) and (avg_temperature < 12.5):
        dsv = 2
    elif (75 <= period_count <= 86) and (12.5 <= avg_temperature < 15.5):
        dsv = 3
    elif (75 <= period_count <= 86) and (avg_temperature >= 15.5):
        dsv = 4
    elif (87 <= period_count <= 96) and (avg_temperature < 12.5):
        dsv = 3
    elif (87 <= period_count <= 96) and (avg_temperature >= 12.5):
        dsv = 4

    return dsv


def tomcast_dsv_lookup(period_count, avg_temperature):

    dsv = -1
    if 0 <= count <= 10:
        dsv = 0
    elif (11 <= period_count <= 14) and (avg_temperature < 20.5):
        dsv = 0
    elif (11 <= period_count <= 14) and (20.5 <= avg_temperature < 25.5):
        dsv = 1
    elif (11 <= period_count <= 14) and (avg_temperature >= 25.5):
        dsv = 0
    elif (15 <= period_count <= 22) and (avg_temperature < 17.5):
        dsv = 0
    elif (15 <= period_count <= 22) and (avg_temperature >= 17.5):
        dsv = 1
    elif (23 <= period_count <= 26) and (avg_temperature < 17.5):
        dsv = 0
    elif (23 <= period_count <= 26) and (17.5 <= avg_temperature < 20.5):
        dsv = 1
    elif (23 <= period_count <= 26) and (20.5 <= avg_temperature < 25.5):
        dsv = 2
    elif (23 <= period_count <= 26) and (avg_temperature >= 25.5):
        dsv = 1
    elif (27 <= period_count <= 34) and (avg_temperature < 20.5):
        dsv = 1
    elif (27 <= period_count <= 34) and (20.5 <= avg_temperature < 25.5):
        dsv = 2
    elif (27 <= period_count <= 34) and (avg_temperature >= 25.5):
        dsv = 1
    elif (35 <= period_count <= 50) and (avg_temperature < 17.5):
        dsv = 1
    elif (35 <= period_count <= 50) and (avg_temperature >= 17.5):
        dsv = 2
    elif (51 <= period_count <= 62) and (avg_temperature < 12.5):
        dsv = 2
    elif (51 <= period_count <= 62) and (12.5 <= avg_temperature < 17.5):
        dsv = 1
    elif (51 <= period_count <= 62) and (17.5 <= avg_temperature < 20.5):
        dsv = 2
    elif (51 <= period_count <= 62) and (20.5 <= avg_temperature < 25.5):
        dsv = 3
    elif (51 <= period_count <= 62) and (avg_temperature >= 25.5):
        dsv = 2
    elif (63 <= period_count <= 82) and (avg_temperature < 17.5):
        dsv = 2
    elif (63 <= period_count <= 82) and (avg_temperature >= 17.5):
        dsv = 3
    elif (83 <= period_count <= 90) and (avg_temperature < 20.5):
        dsv = 3
    elif (83 <= period_count <= 90) and (20.5 <= avg_temperature < 25.5):
        dsv = 4
    elif (83 <= period_count <= 90) and (avg_temperature >= 25.5):
        dsv = 3
    elif (91 <= period_count <= 96) and (avg_temperature < 17.5):
        dsv = 3
    elif (91 <= period_count <= 96) and (avg_temperature >= 17.5):
        dsv = 4

    return dsv


def main():
    print download_data('https://mbagweather.ca/partners/win/mawp15.txt')

main()