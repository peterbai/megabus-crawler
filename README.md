# Megabus Crawler

Retrieves trip details from us.megabus.com site.
Takes origin and destination IDs as search parameters. Defaults to searching for trips leaving today. Optionally accepts a range of search dates. Outputs search results into a sqlite3 database.

- - -

## Running

To use, run MBcrawler.py with valid cityCodes.json and distinations.json files. Search results will be saved to 'searchResults.sqlite' in the same directory.

MBcrawler.py is currently set to search for all trips leaving from 390 (Los Angeles) to 414 (San Francisco) from 2014-06-30 to 2014-07-31.
Edit the code that creates a TripPlan object to adjust these parameters.

* Use getCityCodes.py to generate a cityCodes.json file.
* Use getDestinations.py to generate a destinations.json file.
* Use searchCityID.py to get a city's ID by typing in its name.

## Dependencies

BeautifulSoup, Requests