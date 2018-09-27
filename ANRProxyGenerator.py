import requests
from PIL import Image
from io import BytesIO
import math
import sys
import getopt
import os

base_url = "https://netrunnerdb.com/api/2.0/public/deck/"
root_dir = "C:\\Netrunner\\"
resize_height = 346
resize_width = 243
usage = 'ANRProxyGenerator.py -d <deck id>'


def determineFilename(ID)
	if (ID(:1) == '00' or ID(:1) == '01' or ID(:1) == '03' or ID(:1) == '05' or ID(:1) == '07' or ID(:1) == '09' or ID(:1) == '13' or ID(:1) == '20' or ID(:1) == '22' or ID(:1) == '23' or ID(:1) == '24') :
		filename = root_dir + ID(:1) + "*\\" + ID(2:4) + "*.jpg"
		return filename
	elif (ID(:1) == '02' and ID(:1) == '04' and ID(:1) == '06' and ID(:1) == '08' and ID(:1) == '10' and ID(:1) == '11' and ID(:1) == '12' and ID(:1) == '21') :
		subfolder = str(int(ID(2:4))//20).zfill(2)
		filename = root_dir + ID(:1) + "*\\" + subfolder + "*\\" + ID(2:4) + "*.jpg"
		

def main(argv):
    deck_id = -1
    try:
        opts, args = getopt.getopt(argv, 'd:', ["deckid="]) #Get the deck id from the command line

        for opt, arg in opts:
            if opt in ("-d", "--deckid"):
                deck_id = arg
            else:
                print ("Unsupported argument found!")

        deck_request = requests.get(base_url + str(deck_id))
        if deck_request.status_code == 200:
            deck_data = deck_request.json()
            proxy_list = []

            for card_id, number in deck_data['data'][0]['cards'].items():
                #card_picture = requests.get("http://netrunnerdb.com/card_image/" + card_id + ".png")
				card_filename = root_dir + card_id(0,1) + "*\\" +
				card_picture = Image.open(root_dir + card_id(0,1) +
                resized_card_picture = Image.open(BytesIO(card_picture.content)).convert("RGBA")
                resized_card_picture = resized_card_picture.resize((resize_width, resize_height), Image.LANCZOS)

                # Create a list of all pictures to be printed (including duplicates)
                for cards in range (0, number):
                    proxy_list.append(resized_card_picture)

            proxy_index = 0

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

                sheet.save(str(deck_id) + "_" + str(sheet_count)+ '.png', 'PNG', quality=90)
        else:
            print("Error: Could not retrieve decklist")

    except getopt.GetoptError as e:
        print("Error: " + str(e))
        print(usage)
        sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(usage)
    else:
        main(sys.argv[1:])
