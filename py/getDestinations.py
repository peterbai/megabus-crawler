import requests
import json
import datetime
import os
from sys import exit
from sys import stdout

# ==========================================
# 			Read valid cities
# ==========================================

# set __location__ equal to current python script location
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

jsonFile = __location__ + '/cityCodes.json'	# look for cityCodes.json file in same directory

if os.path.isfile(jsonFile):	# read from cityCodes.json file if it exists. Otherwise, exit.
	with open(jsonFile) as file:
		cityCodesDict = json.load(file)
else:
	print '"cityCodes.json" not found in script directory. Exiting.'
	exit(0)

cityCodesDict.pop("retrievedDate", None)	# remove retrievedDate entry. We will use it in a future version.

# ==========================================
# 			Retrieve valid destinations
# ==========================================

print 'Getting valid destinations from Megabus server...\n0%',

# make our crawler appear normal
custom_headers = {
	'Host' : 'us.megabus.com',
	'Referer' : 'http://us.megabus.com/',
	'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
}

# initialize some stuff
totalNumEntries = len(cityCodesDict)
numRequested = 1
destinationsDict = {}

for originIdNumber in cityCodesDict:
	payload = {'originId': originIdNumber}
	r = requests.get('http://us.megabus.com/support/journeyplanner.svc/GetDestinations', params = payload, headers = custom_headers)
	data = json.loads(r.text)	# decodes json response from server to python object hierarchy.

	# uncomment these two lines to see server's json output:
	# json_encoded = json.dumps(data, indent=4, separators=(',',': '))	# encodes python object back to JSON for pretty printing
	# print json_encoded + '\n'

	destinationsDict[originIdNumber] = []	# initialize empty list as value for current key (origin city ID)

	for destinationItem in data['d']:
		# print originIdNumber + ' : ' + \
		# cityCodesDict[originIdNumber] + ' ---> ' + \
		# destinationItem['idField'] + ' : ' + \
		# destinationItem['descriptionField']

		destinationsDict[originIdNumber].append(destinationItem['idField'])

	# update percent complete
	print '\r', numRequested * 100 / totalNumEntries, '%',
	stdout.flush()	# force print output
	numRequested += 1

# add access date to the dictionary
accessDate = datetime.datetime.now()
dateOut = accessDate.strftime("%Y-%m-%d %H:%M:%S")	# create datetime output in "%Y-%m-%d %H:%M:%S"format
destinationsDict['destRetrievedDate'] = dateOut

# ==========================================
# 			Write valid destinations
# ==========================================

# write the data in json format to destinations.json in same directory
with open(__location__ + '/destinations.json', 'w') as file:
	json.dump(destinationsDict, file, sort_keys = True, indent = 4)