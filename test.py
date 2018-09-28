#import requests
#from PIL import Image
from io import BytesIO
import math
import sys
import getopt
import os
import glob

base_url = "https://netrunnerdb.com/api/2.0/public/deck/"
#root_dir = "C:\\Netrunner\\"
root_dir = "/Users/USERNAME/Downloads/Netrunner/"
resize_height = 346
resize_width = 243
usage = 'ANRProxyGenerator.py -d <deck id>'


def determineFilename(ID) :
    #if (ID(:1) == '00' or ID(:1) == '01' or ID(:1) == '03' or ID(:1) == '05' or ID(:1) == '07' or ID(:1) == '09' or ID(:1) == '13' or ID(:1) == '20' or ID(:1) == '22' or ID(:1) == '23' or ID(:1) == '24') :
    if (ID[0:2] == '00' or ID[0:2] == '01' or ID[0:2] == '03' or ID[0:2] == '05' or ID[0:2] == '07' or ID[0:2] == '09' or ID[0:2] == '13' or ID[0:2] == '20' or ID[0:2] == '22' or ID[0:2] == '23' or ID[0:2] == '24') :
        #filename = glob.glob(root_dir + ID(:1) + "*\\" + ID(2:4) + "*.jpg")
        filename = glob.glob(root_dir + ID[0:2] + "*/" + ID[2:5] + "*.jpg")
        return filename
    elif (ID[0:2] == '02' or ID[0:2] == '04' or ID[0:2] == '06' or ID[0:2] == '08' or ID[0:2] == '10' or ID[0:2] == '11' or ID[0:2] == '12' or ID[0:2] == '21') :
        subfolder = str(int(ID[2:5])//20 + 1).zfill(2)
        print(subfolder)
        #filename = glob.glob(root_dir + ID(:1) + "*\\" + subfolder + "*\\" + ID(2:4) + "*.jpg")
        filename = glob.glob(root_dir + ID[0:2] + "*/" + subfolder + "*/" + ID[2:5] + "*.jpg")
        return filename
    else:
        print ("No Card Found for card ID: " + ID + "!")

currentFilename = determineFilename("02098")
print(currentFilename)
