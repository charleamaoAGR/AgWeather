from datetime import datetime
import os

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


class DailyData:

    def __init__(self, date_var):
        self.date_var = date_var
        self.data = []
        self.period_size = 0

    def add_data(self, time_stamp, temp, RH, rain, avg_ws, avg_wd):
        self.data.append([date_to_hours(time_stamp), temp, RH, rain, avg_ws, avg_wd])
        self.period_size += 1

    def get_date(self):
        return self.date_var

    def get_daily_data(self):
        return self.data

    def get_daily_dsv(self, cumul_dsv):
        dsv = 0

        if self.period_size == 96:
            if cumul_dsv < 18:
                params = self.wisdom_params()
                dsv = wisdom_dsv_lookup(params[0], params[1])
            else:
                params = self.tomcast_params()
                dsv = tomcast_dsv_lookup(params[0], params[1])
        return dsv

    def wisdom_params(self):
        matching_periods = 0
        temp_sum = 0.0
        for each_entry in self.data:
            if each_entry[1] >= 7 and each_entry[2] >= 86:
                matching_periods += 1
                temp_sum += each_entry[1]

        if matching_periods == 0:
            temp_sum = 0
        else:
            temp_sum = temp_sum / matching_periods

        return [matching_periods, temp_sum]

    def tomcast_params(self):
        matching_periods = 0
        temp_sum = 0.0
        for each_entry in self.data:
            if each_entry[2] >= 86 and (9 <= each_entry[1] < 27):
                matching_periods += 1
                temp_sum += each_entry[1]

        if matching_periods == 0:
            temp_sum = 0
        else:
            temp_sum = temp_sum / matching_periods
        return [matching_periods, temp_sum]


class WeatherStation(Packet):

    def __init__(self, name):
        super(WeatherStation, self).__init__(name)
        self.header = [["DateTime", "Temp", "RH", "Rain", "AvgWS", "AvgWD"]]
        self.invalid_data_flag = False
        self.days = []
        self.data_size = 0

    def add_data(self, items):

        if len(items) > 1:

            try:
                date_info = datetime.strptime(items[0], '%Y-%m-%d %H:%M')

                if self.invalid_data_flag == False:
                    if '-7999' in items:
                        self.invalid_data_flag = True
                        print "Station %s flagged for invalid data." % self.id

                temp = float(items[2])
                RH = int(items[3])
                rain = float(items[4])
                avg_ws = float(items[5])
                avg_wd = float(items[6])

                if self.data_size == 0:
                    self.add_date(date_info)
                    self.data[-1].add_data(date_info, temp, RH, rain, avg_ws, avg_wd)
                elif self.data_size > 0:
                    if self.data[-1].get_date().date() == date_info.date():
                        self.data[-1].add_data(date_info, temp, RH, rain, avg_ws, avg_wd)
                    else:
                        self.data[-1].add_data(date_info, temp, RH, rain, avg_ws, avg_wd)  # Add 00:00 data
                        self.add_date(date_info)

            except ValueError:
                print "Station data is invalid for %s. Skipping data entry for this time period." % self.id

    def add_date(self, date_info):
        new_day = DailyData(date_info)
        self.data.append(new_day)
        self.data_size += 1

    def today_cumulative_dsv(self, seed_date):  # Create function to get just today's DSV as well.
        cumul_dsv = 0
        index = 0
        output_txt = open('comparison.txt', 'w+')
        for each_day in self.data:
            if each_day.get_date().date() == seed_date.date():
                break
            index += 1

        for each_day in self.data[index:-1]:  # Index -2 because last item is always an incomplete day.
            daily_dsv = each_day.get_daily_dsv(cumul_dsv)
            cumul_dsv += daily_dsv
            output_txt.write("Station: %s | Date: %s | Daily DSV: %s | Cumulative DSV: %s\n" % (self.id, datetime.strftime(each_day.get_date(), "%Y-%m-%d"), daily_dsv, cumul_dsv))
        output_txt.close()

        return cumul_dsv  # Maybe return DSV straight from table and not just cumulative?

    def today_dsv(self, seed_date):
        return self.data[-2].get_daily_dsv(self.today_cumulative_dsv(seed_date))

    def show_data(self):
        for each_day in self.data:
            print each_day.get_daily_dsv(0)


def date_to_hours(date_var):
    return date_var.hour + date_var.minute/60.0


def wisdom_dsv_lookup(period_count, avg_temperature):

    dsv = 0
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

    dsv = 0
    if 0 <= period_count <= 10:
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


def get_path_dir(directory, file_name):
    cwd = os.getcwd()
    file_base_dir = os.path.join(cwd, directory)
    file_path = os.path.join(file_base_dir, file_name)

    if not os.path.exists(file_base_dir):
        raise Exception('Directory %s does not exist within working directory.' % directory)
        file_path = ""
    if not os.path.exists(file_path):
        raise Exception('File %s does not exist within %s.' % (file_name, directory))
        file_path = ""

    return file_path
