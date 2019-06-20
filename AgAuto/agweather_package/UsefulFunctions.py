import os
import csv
import urllib2
import requests
from tqdm import tqdm


"""
Purpose: The get_path_dir is responsible for returning a string of a valid file path to a file in the AgAuto cwd if
given a valid directory within the AgAuto cwd and a file within the cwd.

Parameters:
    - directory: Must be a folder that exists within the AgAuto cwd.
    - file_name: The file that you want to access within directory.
    - create: If True, then get_path_dir will not care that the file doesn't exist in directory yet as it assumes
    it will be created using the file path that get_path_dir returns.
"""


def get_path_dir(directory, file_name, create=True):
    # Gets the path of the working directory (i.e. AgAuto's working directory).
    cwd = os.getcwd()
    # Add directory to the working directory path.
    file_base_dir = os.path.join(cwd, directory)
    # Add file_name to the new path created above.
    file_path = os.path.join(file_base_dir, file_name)

    # If the directory doesn't exist then raise an Exception.
    if not os.path.exists(file_base_dir):
        raise Exception('Directory %s does not exist within working directory.' % directory)
    # Raise an exception only if the user specifies create = False. Otherwise, assume they will create after.
    if not create:
        if not os.path.exists(file_path):
            raise Exception('File %s does not exist within %s.' % (file_name, directory))

    return file_path


def download_data(url, local_data=False):

    if local_data:
        with open(get_path_dir('raw_output_data', 'mawp_15_test.txt'), 'r') as text_file:
            data = text_file.read().split('\n')[1:-1]
    else:
        response = urllib2.urlopen(url)
        data = response.read().split('\n')[1:-1]

    return data


"""
Purpose: download_txt_request's role is to download any file with 
"""


def download_txt_request(url, file_name, default_folder='input_data'):

    with requests.get(url, stream=True) as r:
        chunkSize = 1024
        with open(get_path_dir(default_folder, file_name), 'wb') as raw_file:
            for chunk in tqdm(iterable=r.iter_content(chunk_size=chunkSize), total=int(r.headers['Content-Length']) / chunkSize, unit='KB', desc="Downloading %s" %file_name):
                raw_file.write(chunk)


def download_grib_request(url, file_name, default_folder='input_data'):

    with requests.get(url, stream=True) as r:
        chunkSize = 1024
        with open(get_path_dir(default_folder, file_name), 'wb') as raw_file:
            for chunk in tqdm(iterable=r.iter_content(chunk_size=chunkSize), unit='KB', desc="Downloading %s" %file_name):
                raw_file.write(chunk)


def split_text_file(file_name, default_folder='input_data', start_index=1, end_index=-1):

    raw_file = open(get_path_dir(default_folder, file_name), 'r')
    output_text = raw_file.read().split('\n')[start_index:end_index]
    raw_file.close()

    return output_text


def convert_input_csv(csv_file_name, output_file_name, input_folder='input_data', output_folder='raw_output_data'):
    with open(get_path_dir(input_folder, csv_file_name), 'r') as potato_csv:
        contents = list(csv.reader(potato_csv, delimiter=','))
        output_file = open(get_path_dir(output_folder, output_file_name), 'w+')
        for each_line in contents:
            output_file.write("%s\n" % ','.join(each_line))
        output_file.close()


def date_to_hours(date_var):
    return date_var.hour + date_var.minute/60.0


def wisdom_dsv_lookup(period_count, avg_temperature_raw):

    if avg_temperature_raw > 7.0:
        avg_temperature = round(avg_temperature_raw)
    else:
        avg_temperature = avg_temperature_raw

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


def tomcast_dsv_lookup(period_count, avg_temperature_raw):

    if avg_temperature_raw > 9.0:
        avg_temperature = round(avg_temperature_raw)
    else:
        avg_temperature = avg_temperature_raw

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
