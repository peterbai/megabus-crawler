from bs4 import BeautifulSoup
from sys import exit
from sys import stdout
from random import choice
from time import sleep
import datetime
import requests
import sqlite3
import json
import os

# ==========================================
# 			Define classes
# ==========================================

class TripPlan(object):
	'''Creates a TripPlan object. Takes input origin and destination as Megabus city ID's.
		Optionally takes datetime objects as search start and end dates. Requires valid cityCodesDict
		and destinationsDict dictionaries.
		Attributes:
			origin,
			destination,
			search_start_date,
			search_end_date
		'''
	
	def __init__(self, input_origin, input_destination, input_search_start_date = None, input_search_end_date = None):

		self.origin = input_origin
		self.destination = input_destination

		# validate origin and destination
		if self.origin in destinationsDict and self.destination in destinationsDict[self.origin]:
			pass
			# print 'Valid origin and destination.'
		else:
			print 'Invalid origin or destination. Exiting.'
			exit(1)

		if input_search_start_date is None:	# if no start date is provided, set to today
			self.search_start_date = datetime.datetime.now()
		else:
			self.search_start_date = input_search_start_date

		if input_search_end_date is None:	# if no end date is provided, set to start date
			self.search_end_date = self.search_start_date
		else:
			self.search_end_date = input_search_end_date

		if self.search_end_date < self.search_start_date:	# raise exception error if end date is before start date
			raise Exception("End date is before start date!")

	def printTripDetails(self):	
		print 'Traveling from %s to %s. Searching from %s to %s' % \
					(cityCodesDict[self.origin], cityCodesDict[self.destination],
					self.search_start_date.strftime('%B %d, %Y'),
					self.search_end_date.strftime('%B %d, %Y') )	# print the output of the strftime method with parameters '%B %d, %Y'.


# ==========================================
# 			Define functions
# ==========================================

def crawl(input_trip_object):

	print 'Crawling!'

	# create wait times (range of seconds)
	rs = range(1,3)

	custom_headers = {
			'Host' : 'us.megabus.com',
			'Referer' : 'http://us.megabus.com/',
			'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
		}

	currentCrawlDate = input_trip_object.search_start_date 		# datetime object

	noTripCount = 0

	while currentCrawlDate <= input_trip_object.search_end_date:

		print 'Waiting...',
		stdout.flush()	# force print output
		sleep(choice(rs))	#random wait time
		megabusDepartureDate = '{d.month}/{d.day}/{d.year}'.format(d = currentCrawlDate)	# string
		print '\rLooking up trips on %s... ' % megabusDepartureDate,
		stdout.flush()	# force print output

		payload = {		# trip search query parameters
			'originCode' : input_trip_object.origin,
			'destinationCode' : input_trip_object.destination,
			'outboundDepartureDate' : megabusDepartureDate,
			'inboundDepartureDate' : '',
			'passengerCount' : '1',
			'transportType' : '0',
			'concessionCount' : '0',
			'nusCount' : '0',
			'outboundWheelchairSeated' : '0',
			'outboundOtherDisabilityCount' : '0',
			'inboundWheelchairSeated' : '0',
			'inboundOtherDisabilityCount' : '0',
			'outboundPcaCount' : '0',
			'inboundPcaCount' : '0',
			'promotionCode' : '',
			'withReturn' : '0'
		}

		url = 'http://us.megabus.com/JourneyResults.aspx'
		r = requests.post(url, params = payload, headers = custom_headers)

		if "No journeys have been found" in r.text:
			if currentCrawlDate == input_trip_object.search_end_date:
				print 'No trips found.'
			elif noTripCount >= 1:
				print 'Still no trips found. Ending Search.'
				exit(0)
			else:
				print 'No trips found. Checking next date...'
				noTripCount += 1

			currentCrawlDate += datetime.timedelta(days = 1)
			continue

		else:
			crawlResults = parseSearchResults(r)

		# add ISO datetime
		addDatetime(crawlResults, currentCrawlDate)

		# write results for current search date to sqlite3 database
		writeDatabase(crawlResults)

		currentCrawlDate += datetime.timedelta(days = 1)

	print 'Search completed.'


def parseSearchResults(r_object):

	soupResults = BeautifulSoup(r_object.text, 'lxml').find_all("ul", class_ = "standard")
	resultsDict = {}
	tripNumber = 0

	# collect trip information
	for entry in soupResults:
		tripDetail = []

		# get departure information
		for departure_string in entry.find("li", class_ = "two").p:
			if not departure_string.extract().strip():		# skip blank lines and use .extract() to ignore <!-- html --> comments.
				continue
			elif departure_string.strip() == ',':	# skip commas
				continue

			tripDetail.append(
				departure_string.strip().replace(u'\xa0', u' ').encode('utf-8')	# replaces non-breaking space with space and converts to unicode.	
			)

		# get arrival information
		for arrival_string in entry.find("li", class_ = "two").find("p", class_ = "arrive"):
			if not arrival_string.extract().strip():
				continue
			elif arrival_string.strip() == ',':
				continue

			tripDetail.append(
				arrival_string.strip().replace(u'\xa0', u' ').encode('utf-8')
			)

		# get price
		tripPrice = entry.find("li", class_ = "five").p.string.strip().encode('utf-8')
		tripDetail.append(tripPrice[1:])	# omit the dollar sign

		# save results
		resultsDict[tripNumber] = tripDetail
		tripNumber += 1

	return resultsDict


def addDatetime(input_resultsDict, input_search_date):
	'''Takes a parsed search result dictionary and adds datetime values in iso format'''

	for key in input_resultsDict:

		departTime = datetime.datetime.strptime(input_resultsDict[key][0], '%I:%M %p')
		departDate = input_search_date
		departDateTime = datetime.datetime.combine(departDate.date(), departTime.time())

		arriveTime = datetime.datetime.strptime(input_resultsDict[key][3], '%I:%M %p')
		arriveDateTime = datetime.datetime.combine(departDate.date(), arriveTime.time())
		
		if arriveDateTime < departDateTime:	# corrects arrival date for redeye trips
			arriveDateTime += datetime.timedelta(days = 1)

		# print 'depart: %s // arrive: %s // duration: %s' % \
		# 	(departDateTime, arriveDateTime, arriveDateTime - departDateTime)

		input_resultsDict[key].append(departDateTime.isoformat())	# this should go into index 7
		input_resultsDict[key].append(arriveDateTime.isoformat())	# this should go into index 8


def writeDatabase(input_resultsDict):
	
	cursor = db.cursor()

	for key in input_resultsDict:

		departTime = input_resultsDict[key][0]
		departCity = input_resultsDict[key][1]
		departLocation = input_resultsDict[key][2]
		arriveTime = input_resultsDict[key][3]
		arriveCity = input_resultsDict[key][4]
		arriveLocation = input_resultsDict[key][5]
		price = input_resultsDict[key][6]
		departDateTime = input_resultsDict[key][7]
		arriveDateTime = input_resultsDict[key][8]

		cursor.execute('''INSERT INTO trips(
							departtime, departcity, arrivetime, arrivecity,	price
						)
						VALUES (?, ?, ?, ?, ?)''',(
							departDateTime, departCity, arriveDateTime, arriveCity, price
						))

		db.commit()

	print '%i results written to database file.' % len(input_resultsDict)


# ===========================================
# 			Read file data
# ===========================================

# set __location__ equal to current python script location
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# look for json files in same directory
cityCodesFile = __location__ + '/cityCodes.json'	
destinationsFile = __location__ + '/destinations.json'

if os.path.isfile(cityCodesFile):	# read from cityCodes.json file if it exists. Otherwise, exit.
	with open(cityCodesFile) as file:
		cityCodesDict = json.load(file)
else:
	print '"cityCodes.json" not found. Exiting.'
	exit(0)

if os.path.isfile(destinationsFile):	# read from cityCodes.json file if it exists. Otherwise, exit.
	with open(destinationsFile) as file:
		destinationsDict = json.load(file)
else:
	print '"destinations.json" not found. Exiting.'
	exit(0)

# remove retrievedDate entries. We will use it in a future version.
cityCodesDict.pop("retrievedDate", None)
destinationsDict.pop("destRetrievedDate", None)


# ===========================================
# 			Initialize database
# ===========================================

db = sqlite3.connect(__location__ + '/searchResults.sqlite')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS trips(id INTEGER PRIMARY KEY,
				departtime TIMESTAMP,
				departcity TEXT,
				arrivetime TIMESTAMP,
				arrivecity TEXT,
				price REAL)''')		# set price as REAL so that sorting works better.

db.commit()


# ===========================================
# 			Create a trip
# ===========================================

start_date = datetime.datetime.strptime('2014-06-30', '%Y-%m-%d')
# start_date = datetime.datetime.today()
end_date = datetime.datetime.strptime('2014-07-31', '%Y-%m-%d')

trip_01 = TripPlan('390', '414', start_date, end_date)
trip_01.printTripDetails()

# Run the search!
crawl(trip_01)