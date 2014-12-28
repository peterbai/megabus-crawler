import json
import os

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

# invert dictionary and convert to lowercase to allow city name searching
cityCodesDictInv = dict([[value.lower(), key] for key, value in cityCodesDict.items()])
# print json.dumps(cityCodesDictInv, sort_keys = True, indent = 4)


# ==========================================
# 			Match user search
# ==========================================

search_input = (raw_input('What city would you like to search?\n> '
				)).lower()	# convert to lowercase for searching

matches = {}
selectedCity = ""

for key, value in cityCodesDictInv.items():
	if search_input in key:
		matches[key] = cityCodesDictInv[key]

if len(matches) <= 0:
	print "No matches found"

elif len(matches) == 1:
	for key, value in matches.items():	# need to use .items() to iterate through key:value pairs. Using for loop to access dictionary key
		print  cityCodesDict[value] # print the Capitalized version.
		selectedCity = value

elif len(matches) <= 10:
	selectionDict = {}	# create new dictionary for selection choices
	matchIndex = 1
	
	print '%i matches:' % len(matches)
	
	for key, value in matches.items():	# need to use .items() to iterate through key:value pairs
		selectionDict[matchIndex] = value	# add dictionary entry with index as key and city ID as value
		print  '%i : %s' % (matchIndex, cityCodesDict[value]) # print the Capitalized version.
		matchIndex += 1

	while True:	# ask user for selection. Check for validity.
		try:
			selection_input = int(raw_input('Please input the number of your selection:\n> '))	# this will throw a ValueError if not a number
			selectedCity = selectionDict[selection_input]	# this will throw a KeyError if selection_input is invalid
			break
		except (KeyError, ValueError):
			print 'Invalid selection.'
			
else:
	print 'More than 10 matches. Please be more specific.'

if selectedCity:
	print 'Selected %s : %s' % (cityCodesDict[selectedCity], selectedCity)