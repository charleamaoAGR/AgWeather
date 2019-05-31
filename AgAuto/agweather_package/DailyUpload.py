from agweather_package import xml_parser as parse
from agweather_package import get_path_dir
from datetime import date, timedelta
from tqdm import tqdm
import csv


urlroot = "http://dd.weather.gc.ca/observations/xml/MB/yesterday/"
MAXTEMP = 2
MINTEMP = 3
PRECIP = 6

"""
Purpose: update_dailyEC updates the DailyEC.csv file with new weather station
data for Environment canada weather stations listed on the config file stations.txt.

NOTE: update_dailyEC will create the DailyEC.csv file if it doesn't exist (i.e. when running the program
at the start of a new growing season.

Parameters:
        default_file - This parameter is set to edit the DailyEC.csv file in the
        same working directory as the script. Can set this parameter to any
        csv file name as long as the files contents follow the same format
        as DailyEC.
"""


def update_dailyEC(default_file="DailyEC.csv"):
    # strdate_dash is yesterday's date, whereby each field is separated by a '-' (E.g. "2019-05-21").
    strdate_dash = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # daily_contents is initialized as the csv header. Will need this if 'DailyEC.csv' doesn't exist.
    daily_contents = [["StationID", "StationName", "Date", "Tmax", "Tmin", "Precip"]]

    # Try opening 'DailyEC.csv' and read its contents. The csv file is created if it doesn't exist.
    # The csv file is created at the end of the getUpdatedDailyData function.
    try:
        daily_csv = open(default_file, 'r')
        daily_contents = list(csv.reader(daily_csv, delimiter=','))
        daily_csv.close()
    except IOError:
        print "No DailyEC.csv found. Creating new csv file and appending."

    # If daily_contents contains data other than the headers, then insert summary data under the right locations.
    if len(daily_contents) > 1:

        # If the process hasn't been ran for more than 1 day, 'dates' contains more dates than just yesterday's date.
        dates = getEarlyDates(daily_contents, strdate_dash)

        # Loops through every date where the dailyUpload program doesn't have data for.
        for each_date in dates:
            updated_daily_contents = [daily_contents.pop(0)]
            getUpdatedDailyData(urlroot, each_date, daily_contents, updated_daily_contents)
            daily_csv = open(default_file, 'r')
            daily_contents = list(csv.reader(daily_csv, delimiter=','))
            daily_csv.close()

    # If daily_contents only contains the headers, then get latest data for each station in 'stations.txt'.
    # Append latest station data to newly created 'DailyEC.csv'.
    else:
        updated_daily_contents = [daily_contents.pop(0)]
        getUpdatedDailyData(urlroot, strdate_dash, daily_contents, updated_daily_contents)


"""
Purpose: dict_summary will return a dictionary that summarizes the max temperature, min temperature, and total precipitation
data from Environment Canada.

Parameters:
    csv_file - this file is the output csv of all xml data from the EC datamart.
"""


def dict_summary(csv_file):
    summary_dict = {}
    read_csv = csv.reader(csv_file, delimiter=',')

    # Loops through each line of the 'output.csv' file and extracts only the date we want.
    for line in read_csv:
        max_temp = line[MAXTEMP]
        min_temp = line[MINTEMP]
        precip = line[PRECIP]
        station_id = line[1].strip()

        if check_station(station_id, get_EC_station_ids()):
            if (max_temp == "" or min_temp == "" or precip == "") and station_id != "" and station_id != "WPO":
                print "Empty fields exist for station ID: %s. Please review Daily EC" % station_id
            if precip.strip() == "Trace":
                precip = "0"
                print "Precipitation for %s was found to be 'Trace'. Check with Frodo and review Daily EC. " % station_id
                print "Setting precipitation as an empty field for %s." % station_id

        summary_dict[station_id] = [max_temp, min_temp, precip]

    return summary_dict


"""
Purpose: get_correct_data allows you to interface with the summary dictionary from the dict_summary function. If given
the desired station ID, the function will return yesterday's max temp, min temp, and total precipitation values.

Parameters:
    station_id - The desired station ID. Note: Some station ID's listed in "stations.txt" are different ID's than
    what is listed in the datamart's xml. IF statements are present throughout the function that maps to the correct ID
    in order to avoid a dictionary key error.
    summary_dict - This parameter contains the output from the function dict_summary.
"""


def get_correct_data(station_id, summary_dict, str_date):
    correct_data = ["", "", ""]

    try:
        if station_id == "YPG":
            correct_data = summary_dict["WPG"]
        elif station_id == "YGM":
            correct_data = summary_dict["PGH"]
        elif station_id == "YWG":
            correct_data = summary_dict["XWG"]
        elif station_id == "YQD":
            correct_data = summary_dict["PQD"]
        elif station_id == "YDN":
            correct_data = summary_dict["WZT"]
        elif station_id == "YBR":
            correct_data = summary_dict["PBO"]
        else:
            correct_data = summary_dict[station_id]
    except KeyError:
        print "KeyError for %s. No data was found at this station for %s." % (station_id, str_date)

    return correct_data


"""
Purpose: get_EC_stations returns a list of the desired Environment Canada stations defined in 'stations.txt', if you
wish to add or remove stations, refer to this text file.
"""


def get_EC_stations():
    stations_list = []
    with open(get_path_dir('config_files', 'stations.txt'), 'r') as stations:
        for each_line in stations:
            stations_list.append(each_line)

    return stations_list


def get_EC_station_ids():
    station_ids = []
    with open(get_path_dir('config_files', 'stations.txt'), 'r') as stations:
        for each_line in stations:
            station_id = each_line.split(':')[0]
            station_ids.append(station_id)

    return station_ids


"""
Purpose: cleanData's purpose is to open filename (which could be "mawp24raw.txt) and remove all instances of
"-7999", "-99", "NAN", and the last line of the textfile.

Parameters:
    filename - this parameter is the file name of the text file to be cleaned.
"""


def cleanData(filename):
    # Change this later to a more general case. Maybe user input?
    try:
        file_wip = open(filename, "r")
        new_contents = ""

        count = 0

        for line in file_wip:
            count += 1

        file_wip.seek(0)

        for line in tqdm(file_wip, desc="Cleaning %s" % filename, total=count):

            # If the length of the line is less than or equal to 1, then don't add it to the output.
            if len(line) > 1:
                append_line = line.replace("-7999", "").replace("-99", "").replace("NAN", "")
                new_contents = new_contents + append_line

        file_wip.close()
        file_wip = open(filename, 'w')
        file_wip.write(new_contents)
        file_wip.close()

    except IOError:
        print "mawp24raw.txt or mawp60raw.txt were not found. Please check directory."


"""
Purpose: getEarlyDates returns a list of the dates in which the DailyEC.csv is missing data. For example if the latest
date in the DailyEC.csv is May 19 and today's date is May 22, the function will return ["2019-05-20", "2019-05-21"].

Parameters:
    dailyList - This is the contents of the DailyEC.csv in list form.
    date_yesterday - This is yesterday's date in the format "YYYY-MM-DD".
"""


def getEarlyDates(dailyList, date_yesterday):
    datesList = []
    yesterday_list = date_yesterday.split('-')

    # Checks if dailyList doesn't only contain the header. Proceeds if it contains more data.
    # Returns blank if dailyList only contains the header.
    if len(dailyList) > 2:
        last_id = dailyList[1][0]
        last_date = dailyList[1][2].split('-')

        # Iterate through all contents of dailyList except the header.
        for each in dailyList[1:-1]:
            new_id = each[0]
            date_latest = each[2].split('-')

            # As soon as a different station_id is detected, date_latest is assumed to be the latest date.
            if last_id != new_id:

                # day_diff is a timedelta variable that gives you the difference between dates.
                # In order to get the difference in days you must type day_diff.days.
                day_diff = date(int(yesterday_list[0]), int(yesterday_list[1]), int(yesterday_list[2])) - date(
                    int(last_date[0]), int(last_date[1]), int(last_date[2]))

                # If the # of days difference is at least 1 day(s) then start generating list of days to get data for.
                if day_diff.days >= 1:
                    for index in range(day_diff.days):
                        new_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2])) + timedelta(
                            days=index + 1)

                        # Converts new_date which is a date variable into string with dashes.
                        datesList.append(new_date.strftime("%Y-%m-%d"))

                # No need to go through rest of dailyList as we already have the latest date and dates list.
                break
            last_date = date_latest

    return datesList


"""
Purpose: The purpose of getUpdatedDailyData is to get and insert the new weather station data into the proper locations
and write the updated contents onto the DailyEC.csv file.

Parameters:
    urlroot - The url containing previous days xml weather station data. Currently points to the EC data mart.
    strdate_dash - This is one of the dates that comes from the getEarlyDates function. Only works with dates in the 
    format "YYYY-MM-DD".
    daily_contents - Similar to getEarlyDates' dailyList parameter. This contains the contents of DailyEC.csv in list
    form.
    updated_daily_contents - Is a list containing only the header. This list gets updated with the data set containing
    new weather station data by the end of the function.
    default_output - The name of the csv file containing the new weather station data from the data mart. Defaults to 
    "output.csv".
"""


def getUpdatedDailyData(urlroot, strdate_dash, daily_contents, updated_daily_contents, default_output="output.csv"):
    date_list = strdate_dash.split('-')

    # Converts strdate_dash into a date variable.
    pure_date = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))

    # Since strdate_dash is decremented by 1, this increments pure_date by 1 day in order to get proper data.
    # In data-mart yesterday's tab, xml files always contain data from the day before the date listed on the file name.
    pure_date = pure_date + timedelta(days=1)

    # Convert pure_date into string format without dashes for use in parse_station.
    strdate = pure_date.strftime("%Y%m%d")
    clean_dict, clean = parse.clean_incoming("fields.txt")

    # results_list and ordered_titles contain the data parsed from the xml files from the data mart.
    results_list, ordered_titles = parse.parse_station(urlroot, strdate, "default", clean_dict=clean_dict, clean=clean)
    parse.csv_out(results_list, ordered_titles, "output.csv")

    # Get the list of desired stations from the stations.txt file.
    stations = get_EC_stations()

    # Grab the new station data from the newly created output.csv file.
    summary_csv = open(get_path_dir('raw_output_data', default_output), 'r')
    summary_dict = dict_summary(summary_csv)
    summary_csv.close()

    # If daily_contents has no data (i.e. there is no DailyEC.csv in the working directory)
    # then add all new station data into updated_daily_contents. updated_daily_contents will only contain the
    # recent data.
    if len(daily_contents) == 0:
        for each_station in stations:
            station_desc = each_station.split(':')
            new_row = ["C%s" % station_desc[0], station_desc[1].strip('\n'), strdate_dash]
            new_row.extend(get_correct_data(station_desc[0], summary_dict, strdate_dash))
            updated_daily_contents.append(new_row)

    # If daily_contents has previous data from previous days then add the new weather station data in the proper
    # locations. The proper location means that the data is inserted along with the rest of that weather station's
    # data. All of the data should be sorted by date (i.e. latest is always last).
    else:
        count = 0
        stations_count = 0
        size = len(daily_contents)

        # Loop through each line in daily_contents.
        for row in tqdm(daily_contents, desc="Updating DailyEC", total=size):

            # Grab the station identifiers (i.e. Station ID, description) along with the new date.
            new_row = ["C%s" % stations[stations_count].split(':')[0], row[1].strip('\n'), strdate_dash]

            # First adds previous weather station data back to the DailyEC.wq
            updated_daily_contents.append(row)

            # If count is still within the allowed index values, then check if consecutive ID's are the same.
            # If the consecutive ID's are different, then insert the new_row here and move on to the next station.
            if count < size - 1:
                if daily_contents[count][0] != daily_contents[count + 1][0]:
                    # Extends new_row to include new weather station data for that ID.
                    new_row.extend(get_correct_data(stations[stations_count].split(':')[0], summary_dict, strdate_dash))
                    updated_daily_contents.append(new_row)
                    stations_count += 1

            # If count is equal to size - 1 then you are at the end of the csv file, insert the new data here.
            else:

                # Extends new_row to include new weather station data for that ID.
                new_row.extend(get_correct_data(stations[stations_count].split(':')[0], summary_dict, strdate_dash))
                updated_daily_contents.append(new_row)
                stations_count += 1

            count += 1

    # Overwrite DailyEC.csv with the newly updated data.
    with open('DailyEC.csv', 'wb') as csv_file:
        daily_ec = csv.writer(csv_file, delimiter=',')
        for each_row in updated_daily_contents:
            daily_ec.writerow(each_row)


def check_station(station_id, stations):
    is_our_station = False

    if station_id in stations:
        is_our_station = True
    elif station_id == "WPG":
        is_our_station = True
    elif station_id == "PGH":
        is_our_station = True
    elif station_id == "XWG":
        is_our_station = True
    elif station_id == "PQD":
        is_our_station = True
    elif station_id == "WZT":
        is_our_station = True
    elif station_id == "PBO":
        is_our_station = True

    return is_our_station
