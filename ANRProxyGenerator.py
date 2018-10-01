import requests
from PIL import Image
from io import BytesIO
import math
import sys
import getopt
import os
import glob

base_url = "https://netrunnerdb.com/api/2.0/public/deck/"
root_dir_W = "C:\\Netrunner\\"
root_dir_U = "/Users/USERNAME/Downloads/Netrunner/"
resize_height = 346 #2000
resize_width = 243 #1434
usage = 'ANRProxyGenerator.py -d <deck id>'



def main(argv):
    opSys = -1
    textFilename = -1
    deck_id = -1
    try:
        opts, args = getopt.getopt(argv, 'o:d:t:', ["os=","deckid=","textfile="]) #Get the deck id from the command line

        for opt, arg in opts:
            if opt in ("-o","--os"):
                opSys = arg
            elif opt in ("-d", "--deckid"):
                deck_id = arg
            elif opt in ("-t", "--textfile"):
                textFilename = arg
            else:
                print ("Unsupported argument found!")

        if (opSys == -1):
            sys.exit("No operating system declared")
        elif (opSys.lower() != "W".lower() and opSys.lower() != "Windows".lower() and opSys.lower() != "U".lower() and opSys.lower() != "Unix".lower()):
            sys.exit("Invalid operating system defined")
        elif (deck_id == -1 and textFilename == -1):
            sys.exit("No deck id or text file defined")

    except getopt.GetoptError as e:
        print("Error: " + str(e))
        print(usage)
        sys.exit(2)

    proxy_list = []

    if (deck_id != -1):
        try:
            deck_request = requests.get(base_url + str(deck_id))
        except:
            sys.exit("Unable to download deck list for deck ID = " + deck_id + "!\n")
        if deck_request.status_code == 200:
            try:
                deck_data = deck_request.json()
            except:
                sys.exit("Unable to parse deck list for deck ID = " + deck_id + "!\n")
            for card_id, number in deck_data['data'][0]['cards'].items():
                card_filename = determineFilename(card_id,opSys)
                #print(card_filename)
                try:
                    card_picture = Image.open(card_filename)
                    #print(card_picture)
                    #resized_card_picture = Image.open(BytesIO(card_picture.content)).convert("RGBA")
                    resized_card_picture = card_picture.resize((resize_width, resize_height), Image.LANCZOS)
                except:
                    print("Failed to open/resize image for card id \"" + card_id + "\"!\n")

                try:
                    # Create a list of all pictures to be printed (including duplicates)
                    for cards in range (0, number):
                        #print(resized_card_picture)
                        proxy_list.append(resized_card_picture)
                except:
                    print("Unable to append card with card ID " + card_id + "!\n")

        else:
            sys.exit("Failed attempt to download deck list for deck ID = " + deck_id + "!\n")

    elif (textFilename != -1):
        try:
            card_file = open(textFilename, 'r')
            card_list = card_file.readlines()
            card_file.close()
        except:
            sys.exit("Unable to open/read card lists file \"" + textFilename + "\"!\n")

        for lineNum, lineText in enumerate(card_list):
            #print(lineText)
            card_filename = -1
            try:
                lineText.replace(" ","")
                card_id = lineText[0:5]
                #print(card_id)
            except:
                print ("Unable to extract a card id from line " + lineNum + ".\n")
            if (len(card_id)==5):
                card_filename = determineFilename(card_id,opSys)
                #print(card_filename)
            else:
                print("Invalid card id on line " + str(lineNum) + ".\n")
            #if(card_filename):
            try:
                card_picture = Image.open(card_filename)
                #resized_card_picture = Image.open(BytesIO(card_picture.content)).convert("RGBA")
                resized_card_picture = card_picture.resize((resize_width, resize_height), Image.LANCZOS)
            except:
                print("Failed to open/resize image for card id \"" + card_id + "\"!\n")

            try:
                # Create a list of all pictures to be printed (including duplicates)
                if (lineText[5] == ","):
                    endOfLine = lineText.find("\\n")
                    if (endOfLine == -1):
                        endOfLine = len(lineText) + 1
                    for cards in range (0, int(lineText[6:endOfLine])):
                        proxy_list.append(resized_card_picture)
                else:
                    proxy_list.append(resized_card_picture)
            except:
                print("Unable to append card with card ID " + card_id + "!\n")

    else:
        sys.exit("Error: Could not retrieve decklist")

    proxy_index = 0
    #print(len(proxy_list))
    for sheet_count in range (0, math.ceil(len(proxy_list)/9)): #how many pages do we need?
        sheet = Image.new('RGBA', (resize_width *3, resize_height * 3)) #a sheet is 3 rows of 3 cards
        y_offset = 0
        # Fill three rows of three images
        rows = [Image.new('RGBA', (resize_width * 3, resize_height))] * 3
        for row in rows:
            x_offset = 0

            for j in range (proxy_index, proxy_index+3):
                if j >= len(proxy_list):
                    break
                row.paste(proxy_list[j], (x_offset,0))
                x_offset += resize_width

            # Combine rows vertically into one image
            sheet.paste(row, (0, y_offset))
            y_offset += resize_height
            proxy_index += 3
            if proxy_index >= len(proxy_list):
                break


        if (deck_id != -1):
            try:
                sheet.save(str(deck_id) + "_" + str(sheet_count)+ '.png', 'PNG', quality=90)
            except:
                print("Unable to save sheet " + str(deck_id) + "_" + str(sheet_count)+ ".png")
        else:
            try:
                sheet.save("Text_File_proxies_" + str(sheet_count)+ '.png', 'PNG', quality=90)
            except:
                print("Unable to save sheet Text_File_proxies_" + str(sheet_count)+ ".png")


def determineFilename(ID,OS) : #get the filename for a card
    filename = []
    if (ID[0:2] == '00' or ID[0:2] == '01' or ID[0:2] == '03' or ID[0:2] == '05' or ID[0:2] == '07' or ID[0:2] == '09' or ID[0:2] == '13' or ID[0:2] == '20' or ID[0:2] == '22' or ID[0:2] == '23' or ID[0:2] == '24') :
        try:
            if (OS.lower() == "W".lower() or OS.lower() == "Windows".lower()):
                filename = glob.glob(root_dir_W + ID[0:2] + "*\\" + ID[2:5] + "*.jpg")
            else:
                filename = glob.glob(root_dir_U + ID[0:2] + "*/" + ID[2:5] + "*.jpg")
        except:
            print ("Could not find card with ID = " + ID + ".\n")
    elif (ID[0:2] == '02' or ID[0:2] == '04' or ID[0:2] == '06' or ID[0:2] == '08' or ID[0:2] == '10' or ID[0:2] == '11' or ID[0:2] == '12' or ID[0:2] == '21') :
        try:
            subfolder = str((int(ID[2:5])-1)//20 + 1).zfill(2)
            #print(subfolder)
            if (OS.lower() == "W".lower() or OS.lower() == "Windows".lower()):
                filename = glob.glob(root_dir_W + ID[0:2] + "*\\" + subfolder + "*\\" + ID[2:5] + "*.jpg")
            else:
                filename = glob.glob(root_dir_U + ID[0:2] + "*/" + subfolder + "*/" + ID[2:5] + "*.jpg")
        except:
            print ("Could not find card with ID = " + ID + ".\n")
    else:
        print ("Could not find set folder for card ID: " + ID + "!\n")
    #print(filename)
    if ( len(filename) > 1 ):
        print ("WARNING: Multiple filenames found for card ID = " + ID + "!\n")
    try:
        return filename[0]
    except:
        print ("Could not find card with ID = " + ID + ".\n")



if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(usage)
    else:
        main(sys.argv[1:])
