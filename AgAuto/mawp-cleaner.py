# -*- coding: utf-8 -*-
"""
Created on Thu May  9 11:51:24 2019

@author: Tojo
"""

import os
from pathlib import Path

def cleanData(filename):
    
    #dirpath = os.path.join(os.getcwd(),filename)
    
    #Change this later to a more general case. Maybe user input?
    file = open(r'C:/Users/CAmao/Documents/Project_1/dist/%s' %filename , "r")
    new_contents = ""
    
    for line in file:
        
        append_line = ""
        if len(line) > 1:
            append_line = line.replace("-7999", "").replace("-99", "")
        new_contents = new_contents + append_line
        
    file.close()
    file = open(filename, 'w')
    file.write(new_contents)
    file.close()
    
      

def main():
    file_24 = "mawp24raw.txt"
    file_60 = "mawp60raw.txt"
    cleanData(file_24)
    cleanData(file_60)
   # dirpath = os.getcwd()
    #print(r'%s\%s' %(dirpath,file_24))

#if line[0] == '"':
main()

