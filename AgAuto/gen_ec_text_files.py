from agweather_package import xml_parser as parse
from agweather_package import get_path_dir

def main():
    daily_data_array = parse.grab_desired_xml_data('daily')
    hourly_data_array = parse.grab_desired_xml_data('hourly')
    id_dictionary = parse.station_id_dictionary('mbag_id')
    desc_dictionary = parse.station_id_dictionary('desc')

    for each_id in id_dictionary.keys():
        file_name_60 = desc_dictionary[each_id] + '60' + '.txt'
        file_name_24 = desc_dictionary[each_id] + '24' + '.txt'
        with open(get_path_dir('output_files', file_name_24), 'w+') as daily_file:
            daily_file.write(parse.gen_string_rep(daily_data_array.get_data(each_id)))

        with open(get_path_dir('output_files', file_name_60), 'w+') as hourly_file:
            hourly_file.write(parse.gen_string_rep(hourly_data_array.get_data(each_id)))


main()
