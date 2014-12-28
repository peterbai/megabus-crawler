import requests
import json
import datetime
import os
from bs4 import BeautifulSoup

custom_headers = {
	'Host' : 'us.megabus.com',
	'Referer' : 'http://us.megabus.com/',
	'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
}

r = requests.get('http://us.megabus.com', headers = custom_headers)
homePage = BeautifulSoup(r.text, 'lxml')
cityData = homePage.find("select", class_ = "ddl-origin").find_all("option")

# create a dictionary of orgin IDs and their respective city names
cityCodesDict = {}

for tag in cityData:
	#  the "value" attribute in each tag is the origin ID
	cityCodesDict[tag['value']] = tag.text	# adds { city origin ID : city name } to dictionary

cityCodesDict.pop("0", None)	# remove entry at key "0" ("Select origin"). If it's not found, return "None"

# add access date to the dictionary
accessDate = datetime.datetime.now()
dateOut = accessDate.strftime("%Y-%m-%d %H:%M:%S")	# create datetime output in "%Y-%m-%d %H:%M:%S"format
cityCodesDict['retrievedDate'] = dateOut

# set __location__ equal to current python script location
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# write the data in json format to cityCodes.json in same directory
with open(__location__ + '/cityCodes.json', 'w') as file:		# 'w' truncates the file to zero.
	json.dump(cityCodesDict, file, sort_keys = True, indent = 4)

# to create a datetime object from a saved string in format "%Y-%m-%d %H:%M:%S", use the following line:
# dateRead = datetime.datetime.strptime('2014-04-17 21:53:00', "%Y-%m-%d %H:%M:%S")