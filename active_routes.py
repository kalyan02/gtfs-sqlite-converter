import os, csv, re, difflib, math, sys, time, json

class CSV(object):
	def __init__(self, file_name, map_fields=1):
		self.file_name = file_name
		self.fh = open( file_name, "r" )
		self.csv = csv.reader( self.fh )
		self.map_fields = map_fields
		if self.map_fields:
			self.fields = self.csv.next()

	def next(self):
		next_row = self.csv.next()
		if self.map_fields:
			return { name : value for name, value in zip(self.fields,next_row) }

		return next_row
	def get_list_map(self):
		rows = []
		while True:
			try:
				row = self.next() 
				rows.append(row)
			except Exception, e:
				break
		return rows
	def rows(self):
		return self.get_list_map()


cd = CSV('calendar_dates.txt').rows()
trips = CSV('trips.txt').rows()
# cd_list = cd.rows()
# for each in cd_list:
# 	print each['service_id'], each['date'], time.mktime(time.strptime(each['date'],"%Y%m%d"))

############ ALL_ROUTES ############ 
# rl = CSV('routes.txt').rows()
# print json.dumps(rl,indent=4)

############ ROUTE_STOPS_MAP ############ 
"""
Each city uses the data format in a different way
Some use exceptions to define the actuals
Some use calendar to define repeating travels


Amsterdam:
- Uses calendar dates for this
- Get atleast 1 service code per route type in the span of 1 week
- Get atleast 1 trip code for a service code
"""
print '-'
route_id = 'GVB|10'
route_10_trips = filter( lambda item: item['route_id'] == route_id, trips )
route_10_trip_ids = set([ each['trip_id'] for each in route_10_trips ])


print len(trips)
print len(route_10_trips)
print len(route_10_trip_ids)

route_10_stop_times = [] #filter( lambda item: item['trip_id'] in route_10_trip_ids, st )
route_10_trip_stops = {}

st_h = CSV('stop_times.txt')
while True:
	try:
		row = st_h.next()
		trip_id = row['trip_id']

		if trip_id in route_10_trip_ids:
			if not route_10_trip_stops.has_key(trip_id):
				route_10_trip_stops[trip_id] = []
			route_10_trip_stops[ trip_id ].append( row )
	except:
		break

route_10_trip_stops_counts = [ len(route_10_trip_stops[each]) for each in route_10_trip_stops ]
for each in set(route_10_trip_stops_counts):
	_cnt = route_10_trip_stops_counts.count(each)
	_tc = len(route_10_trip_stops_counts) + 0.0
	_p = "%0.2f" % (_cnt/_tc)
	print each, _p, _cnt

accepted_trip_type = max(route_10_trip_stops_counts)
good_route_10_trip_stops = filter( lambda item: len(item) == accepted_trip_type, route_10_trip_stops )
print len(good_route_10_trip_stops)

init_trip = good_route_10_trip_stops.pop()
init_trip_stops = [ trip['stop_id'] for trip in route_10_trip_stops[init_trip] ]
print init_trip_stops
for each_trip in good_route_10_trip_stops:
	each_trip_stops = [ trip['stop_id'] for trip in route_10_trip_stops[each_trip] ]
	print each_trip, set(init_trip_stops) - set(each_trip_stops), set(each_trip_stops) - set(init_trip_stops)


# print route_10_trip_stops[ good_route_10_trip_stops[0] ]

# print 'last', len(route_10_trip_stops)




# for each in route_10_trips:
# 	print each['trip_id'], each['trip_headsign']
# return all stop_ids
# using calendar_dates
# -> get trip_ids
#   -> get trip service code for the day
#      -> using stops.txt -> get all stops
