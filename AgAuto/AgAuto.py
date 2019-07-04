# -*- coding: utf-8 -*-
"""
Created on Tue May 14 11:27:19 2019

@author: CAmao

Purpose: AgAuto serves as the main program that allows you to interface with
the different automation programs for AgWeather.

Date modified: Tue May 21 2019
"""

from agweather_package import PotatoBlight as potato
from agweather_package import DailyUpload as daily
from agweather_package import get_path_dir
from pyfiglet import Figlet
from tqdm import tqdm
from subprocess import call
from os import getcwd, path
from time import sleep
import requests

"""
Purpose: user_in() serves as the user interface for AgAuto. The function
will first print a list of choices that are available. Typing out the 
explicit name of a possible choice will either run a program or quit,
if the choice is 'q'.
"""


def user_in():

    rendered_text = Figlet(font='slant')
    print rendered_text.renderText('AgAuto')

    choices = ["dailyUpload", "mawpCleaner", "debug", "calcPotatoDSV", "q"]
    print "[1] dailyUpload\n[2] mawpCleaner \n[3] calcPotatoDSV\n[4] debug\n[q] Quit"
    choice = ''

    # Program will keep asking for which programs to run until user inputs 'q'.
    while choice != 'q':
        choice = raw_input("Which program do you want to run?:")

        if choice == 'dailyUpload':
            daily.update_dailyEC()
            file_24 = "mawp24raw.txt"
            file_60 = "mawp60raw.txt"
            daily.cleanData(file_24)
            daily.cleanData(file_60)
            daily.gen_Bat_file()
            in_me = False
            while not in_me:
                in_me = daily.in_managed_environment()
                sleep(4)
            if in_me:
                call(path.join(getcwd(), 'AgAuto_batch.bat'))

        elif choice == 'mawpCleaner':
            file_24 = "mawp24raw.txt"
            file_60 = "mawp60raw.txt"
            daily.cleanData(file_24)
            daily.cleanData(file_60)
        elif choice == 'calcPotatoDSV':
            potato.show_all_stations_dsv()
        elif choice == 'debug':
            debug()
        elif choice not in choices:
            print "Input error. Please pick from list of commands.\n"
        print '\n'


def debug():
    in_ME = False
    while not in_ME:
        in_ME = daily.in_managed_environment()
    if in_ME:
        call(path.join(getcwd(), 'AgAuto_batch.bat'))


def main():
    # update_dailyEC()
    user_in()
    

main()
