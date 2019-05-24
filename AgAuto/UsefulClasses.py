from datetime import datetime


class Packet(object):

    def __init__(self, name):
        self.id = name
        self.data = []
        self.data_size = 0

    def get_data(self):
        return self.data

    def get_size(self):
        return self.data_size

    def get_id(self):
        return self.id


class WeatherStation(Packet):

    def __init__(self, name):
        super(WeatherStation, self).__init__(name)
        self.header = [["DateTime", "Temp", "RH", "Rain", "AvgWS", "AvgWD"]]

    def add_data(self, item):
        items = item.split(',')

        if len(items) > 1:
            date_info = datetime.strptime(items[0], '%Y-%m-%d %H:%M')
            temp = float(items[2])
            RH = int(items[3])
            rain = float(items[4])
            avg_ws = float(items[5])
            avg_wd = float(items[6])
            self.data.append([date_info, temp, RH, rain, avg_ws, avg_wd])



    def show_data(self):
        print self.header
        print self.data

