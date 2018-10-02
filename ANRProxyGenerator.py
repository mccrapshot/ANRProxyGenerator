import requests
from PIL import Image
from io import BytesIO
import math
import sys
import getopt
import os
import platform
import glob

base_url = "https://netrunnerdb.com/api/2.0/public/deck/"
root_dir_W = "C:\\Netrunner\\"
root_dir_U = "/Users/"
resize_height = 346 #2000
resize_width = 243 #1434
usage = 'ANRProxyGenerator.py -o <operating system> -d <deck id> -t <text file>'



def main(argv):
    opSys = -1
    textFilename = -1
    deck_id = -1
    try:
        opts, args = getopt.getopt(argv, 'd:t:', ["deckid=","textfile="]) #Get the deck id and/or text file from the command line

        for opt, arg in opts:
            if opt in ("-d", "--deckid"):
                deck_id = arg
            elif opt in ("-t", "--textfile"):
                textFilename = arg
            else:
                print ("Unsupported argument found!")

        if (deck_id == -1 and textFilename == -1):
            sys.exit("No deck id or text file defined!")

    except getopt.GetoptError as e:
        print("Error: " + str(e))
        print(usage)
        sys.exit(2)
    try:
        opSys = platform.system()
    except:
        sys.exit("Unable to determine operating system! (Necessary for proper filename formatting)")

    if (opSys != "Windows" and opSys != "Linux" and opSys != "Darwin"):
        sys.exit("Sorry I didn't plan on this OS. Not sure what proper file name formatting should be.")

    proxy_list = []

    if (deck_id != -1):
        try:
            deck_request = requests.get(base_url + str(deck_id))
        except requests.exceptions.RequestException as e:
            print("Error: " + str(e))
            sys.exit("Unable to download deck list for deck ID = " + deck_id + "!\n")
        if deck_request.status_code == 200:
            try:
                deck_data = deck_request.json()
            except:
                sys.exit("Unable to parse deck list for deck ID = " + deck_id + "!\n")
            for card_id, number in deck_data['data'][0]['cards'].items(): #loop through deck list adding card images to proxy_list
                card_filename = determineFilename(card_id,opSys)
                if (not card_filename): #end this pass if no good card value found
                    continue
                #print(card_filename)
                try:
                    card_picture = Image.open(card_filename)
                    #print(card_picture)
                    #resized_card_picture = Image.open(BytesIO(card_picture.content)).convert("RGBA")
                    resized_card_picture = card_picture.resize((resize_width, resize_height), Image.LANCZOS)
                except:
                    print("Failed to open/resize image for card id \"" + card_id + "\"!\n")
                    continue

                if (not resized_card_picture): #end this pass if unable to load card image
                    continue
                try:
                    # Create a list of all pictures to be printed (including duplicates)
                    for cards in range (0, number):
                        #print(resized_card_picture)
                        proxy_list.append(resized_card_picture)
                except:
                    print("Unable to append card with card ID " + card_id + "!\n")

            endOfDecklistProxies = len(proxy_list)

        else:
            sys.exit("Failed attempt to download deck list for deck ID = " + deck_id + "!\n")

    if (textFilename != -1):
        try:
            card_file = open(textFilename, 'r')
            card_list = card_file.readlines()
            card_file.close()
        except:
            sys.exit("Unable to open/read card lists file \"" + textFilename + "\"!\n")

        for lineNum, lineText in enumerate(card_list): #add all card images for cards in in text list to proxy_list
            #print(lineText)
            card_filename = -1
            card_id = -1
            try:
                cleanedLineText = "".join(lineText.split())
                if (not cleanedLineText):
                    continue
                if (cleanedLineText[0:5].isnumeric()):
                    card_id = cleanedLineText[0:5]
                else:
                    print("Line text \"" + cleanedLineText + "\" contains an invalid card id on line number " + str(lineNum) + ".\n")
                    continue
            except:
                print ("Unable to extract a card id from line " + str(lineNum) + ". Line text was \"" + lineText + "\"\n")
                continue

            #print(card_id)
            card_filename = determineFilename(card_id,opSys)
            if (not card_filename): #end this pass if no good card value found
                continue
            #print(card_filename)
            try:
                card_picture = Image.open(card_filename)
                #resized_card_picture = Image.open(BytesIO(card_picture.content)).convert("RGBA")
                resized_card_picture = card_picture.resize((resize_width, resize_height), Image.LANCZOS)
            except:
                print("Failed to open/resize image for card id \"" + card_id + "\"!\n")
                continue

            if (not resized_card_picture): #end this pass if unable to load card image
                continue

            if (len(cleanedLineText) > 5):
                # Create a list of all pictures to be printed (including duplicates)
                if (cleanedLineText[5] == "," or cleanedLineText[5] == ";" or cleanedLineText[5] == ":"):
                    startOfCardCount = 6
                elif (cleanedLineText[5].isnumeric()):
                    startOfCardCount = 5
                else:
                    startOfCardCount = -1
                if (startOfCardCount != -1):
                    endOfLine = len(cleanedLineText) + 1
                    try:
                        if (cleanedLineText[startOfCardCount:endOfLine].isnumeric()):
                            for cards in range (0, int(cleanedLineText[startOfCardCount:endOfLine])):
                                proxy_list.append(resized_card_picture)
                        else:
                            print(cleanedLineText[startOfCardCount:endOfLine] + " is not a number. Only adding one card for card id " + card_id + ".\n")
                            proxy_list.append(resized_card_picture)
                    except:
                        print("Unable to append card with card ID " + card_id + "!\n")
                else:
                    try:
                        proxy_list.append(resized_card_picture)
                        print("Invalid character \"" + cleanedLineText[5] + "\" after card id " + card_id + ". Only adding one card.\n")
                    except:
                        print("Unable to append card with card ID " + card_id + "!\n")
            else:
                try:
                    proxy_list.append(resized_card_picture)
                except:
                    print("Unable to append card with card ID " + card_id + "!\n")


    proxy_index = 0
    #print(len(proxy_list))

    if (deck_id != -1):
        for sheet_count in range (0, math.ceil(endOfDecklistProxies/9)): #how many pages do we need?
            if (endOfDecklistProxies - proxy_index > 9):
                lastIndexForSheet = proxy_index + 9
            else:
                lastIndexForSheet = endOfDecklistProxies
            current_sheet = buildProxySheet(proxy_list,proxy_index,lastIndexForSheet)
            if(lastIndexForSheet != endOfDecklistProxies):
                proxy_index += 9
            else:
                proxy_index = endOfDecklistProxies

            try:
                current_sheet.save(str(deck_id) + "_" + str(sheet_count)+ '.png', 'PNG', quality=90)
            except:
                print("Unable to save sheet " + str(deck_id) + "_" + str(sheet_count)+ ".png")
    if (textFilename != -1):
        startOfTextFileProxies = proxy_index
        for sheet_count in range (0, math.ceil((len(proxy_list)-startOfTextFileProxies)/9)): #how many pages do we need?
            if (len(proxy_list) - proxy_index > 9):
                lastIndexForSheet = proxy_index + 9
            else:
                lastIndexForSheet = len(proxy_list)
            current_sheet = buildProxySheet(proxy_list,proxy_index,lastIndexForSheet)
            proxy_index += 9

            try:
                current_sheet.save("Text_File_proxies_" + str(sheet_count)+ '.png', 'PNG', quality=90)
            except:
                print("Unable to save sheet Text_File_proxies_" + str(sheet_count)+ ".png")

def buildProxySheet(listOfProxies,startIndex,EndIndex):
    index = startIndex
    sheet = Image.new('RGBA', (resize_width *3, resize_height * 3)) #a sheet is 3 rows of 3 cards
    y_offset = 0
    # Fill three rows of three images
    rows = [Image.new('RGBA', (resize_width * 3, resize_height))] * 3
    for row in rows:
        x_offset = 0
        for j in range (index, index+3):
            if j >= EndIndex:
                break
            row.paste(listOfProxies[j], (x_offset,0))
            x_offset += resize_width
         # Combine rows vertically into one image
        sheet.paste(row, (0, y_offset))
        y_offset += resize_height
        index += 3
        if index >= EndIndex:
            break

    return sheet

def determineFilename(ID,OS) : #get the filename for a card
    filename = []
    if (ID[0:2] == '00' or ID[0:2] == '01' or ID[0:2] == '03' or ID[0:2] == '05' or ID[0:2] == '07' or ID[0:2] == '09' or ID[0:2] == '13' or ID[0:2] == '20' or ID[0:2] == '22' or ID[0:2] == '23' or ID[0:2] == '24') :
        try:
            if (OS == "Windows"):
                filename = glob.glob(root_dir_W + ID[0:2] + "*\\" + ID[2:5] + "*.jpg")
            else:
                filename = glob.glob(root_dir_U + ID[0:2] + "*/" + ID[2:5] + "*.jpg")
        except:
            print ("Could not find card with ID = " + ID + ".\n")
    elif (ID[0:2] == '02' or ID[0:2] == '04' or ID[0:2] == '06' or ID[0:2] == '08' or ID[0:2] == '10' or ID[0:2] == '11' or ID[0:2] == '12' or ID[0:2] == '21') :
        try:
            subfolder = str((int(ID[2:5])-1)//20 + 1).zfill(2)
            #print(subfolder)
            if (OS == "Windows"):
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
    if (filename):
        try:
            return filename[0]
        except:
            print ("Could not pass filename for card with ID = " + ID + ".\n")
    else:
        return filename



if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(usage)
    else:
        main(sys.argv[1:])
