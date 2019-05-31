"""
Created on Fri May 31 9:00:00 2019

@author: CAmao

Purpose: PotatoBlight contains the necessary functions to calculate all station DSVs listed in
'2018 Permanent Stations.xlsx'.

Date modified: Fri May 31 2019
"""

from datetime import datetime, timedelta
from UsefulFunctions import get_path_dir
from UsefulFunctions import date_to_hours
from UsefulFunctions import wisdom_dsv_lookup
from UsefulFunctions import tomcast_dsv_lookup
import os

# CONSTANTS
MAXIMUM_PERIOD_SIZE = 96
MIN_ALLOWABLE_PERIOD_SIZE = 86
RH_CUTOFF = 86
WISDOM_DSV_CUTOFF = 18
WISDOM_LOW_TEMP_CUTOFF = 7
TOMCAST_LOW_TEMP_CUTOFF = 9
TOMCAST_HIGH_TEMP_CUTOFF = 27
DATE_INDEX = 0
ID_INDEX = 1
TEMP_INDEX = 2
RH_INDEX = 3
RAIN_INDEX = 4
AVG_WS_INDEX = 5
AVG_WD_INDEX = 6


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
        self.avg_temp = 0.0
        self.period_count = 0

    def add_data(self, time_stamp, temp, RH, rain, avg_ws, avg_wd):
        self.data.append([time_stamp, temp, RH, rain, avg_ws, avg_wd])
        self.period_size += 1

    def get_date(self):
        return self.date_var

    def get_earliest_date(self):
        return self.data[0][0]

    def get_daily_dsv(self, cumul_dsv):
        dsv = 0

        if self.period_size > MIN_ALLOWABLE_PERIOD_SIZE:  # If missing 10 periods then ignore.
            if cumul_dsv < WISDOM_DSV_CUTOFF:
                params = self.wisdom_params()
                self.period_count = params[0]
                self.avg_temp = params[1]
                dsv = wisdom_dsv_lookup(params[0], params[1])
            else:
                params = self.tomcast_params()
                self.period_count = params[0]
                self.avg_temp = params[1]
                dsv = tomcast_dsv_lookup(params[0], params[1])
        return dsv

    def wisdom_params(self):
        matching_periods = 0
        temp_sum = 0.0
        for each_entry in self.data:
            if each_entry[1] >= WISDOM_LOW_TEMP_CUTOFF and each_entry[2] >= RH_CUTOFF:
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
            if each_entry[2] >= RH_CUTOFF and (TOMCAST_LOW_TEMP_CUTOFF <= each_entry[1] < TOMCAST_HIGH_TEMP_CUTOFF):
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
        self.output_txt = ""

    def add_data(self, items):

        if len(items) > 1:

            try:
                date_info = datetime.strptime(items[DATE_INDEX], '%Y-%m-%d %H:%M')

                temp = float(items[TEMP_INDEX])
                RH = int(items[RH_INDEX])
                rain = float(items[RAIN_INDEX])
                avg_ws = float(items[AVG_WS_INDEX])
                avg_wd = float(items[AVG_WD_INDEX])

                if self.data_size == 0 and date_to_hours(date_info) == 12.25:  # Check if 12:15 PM
                    self.add_date(date_info + timedelta(days=1))  # Creates and adds new DailyData object.
                    self.data[-1].add_data(date_info, temp, RH, rain, avg_ws, avg_wd)
                elif self.data_size > 0:
                    if self.check_valid_range(self.data[-1].get_earliest_date(), date_info):
                        self.data[-1].add_data(date_info, temp, RH, rain, avg_ws, avg_wd)
                    else:
                        if self.data[-1].period_size <= MIN_ALLOWABLE_PERIOD_SIZE and not self.invalid_data_flag:
                            self.invalid_data_flag = True
                        self.add_date(date_info + timedelta(days=1))
                        self.data[-1].add_data(date_info, temp, RH, rain, avg_ws, avg_wd)  # Add 12:15 PM data

            except ValueError:
                print "Station data is invalid for %s. Skipping data entry for this time period." % self.id

    def add_date(self, date_info):
        new_day = DailyData(date_info)
        self.data.append(new_day)
        self.data_size += 1

    def today_dsv_package(self, seed_date):  # Create function to get just today's DSV as well.
        index = self.get_date_index(seed_date)
        cumul_dsv = 0
        for each_day in self.data[index:]:  # Index -2 because last item is always an incomplete day.
            daily_dsv = each_day.get_daily_dsv(cumul_dsv)
            cumul_dsv += daily_dsv
            self.output_txt = self.output_txt + ("Station: %s | Date: %s | Daily DSV: %s | Cumulative DSV: %s | Count: %s | Avg. Temp: %.2f\n"
                                                 % (self.id, datetime.strftime(each_day.get_date(), "%Y-%m-%d"), daily_dsv,
                                                       cumul_dsv, each_day.period_count, each_day.avg_temp))

        return cumul_dsv, self.output_txt  # Maybe return DSV straight from table and not just cumulative?

    def today_dsv(self, seed_date):  # What about for beginning of season where you have less than 1 day of data?!

        cumul_dsv, output_txt = self.today_dsv_package(seed_date)

        if self.data[-1].period_size == MAXIMUM_PERIOD_SIZE:
            today_dsv = self.data[-1].get_daily_dsv(cumul_dsv)
        else:
            today_dsv = self.data[-2].get_daily_dsv(cumul_dsv)

        return today_dsv, cumul_dsv, output_txt

    def get_date_index(self, seed_date):
        index = 0
        for each_day in self.data:
            if each_day.get_date().date() == seed_date.date():
                break
            index += 1
        return index

    def check_valid_range(self, daily_date, new_date):
        daily_date_reset = datetime.strptime(daily_date.strftime("%Y-%m-%d") + " 12:00", "%Y-%m-%d %H:%M") + timedelta(days=1)
        return new_date <= daily_date_reset



