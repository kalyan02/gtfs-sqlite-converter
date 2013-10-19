gtfs-sqlite-converter
=====================

Convert GTFS data set into a sqlite database to make it convenient for querying/extracting data, etc.

## gtfs_auto_db.py

Creates the main sqlite database required from the data set

## get_stops.py 

Extract the gvb's stop and shape data for Amsterdam's GTFS data set

`gtfs_auto_db.py` must be run before running this script

## active_routes.py

Sometimes the routes are cut short due to maintainance and other isuses. This scripts looks at all the stops that were used by all transit runs of a particular route and extracts the longest and most used route/stops. The extracted data is stored into set of json files

`gtfs_auto_db.py` must be run before running this script
