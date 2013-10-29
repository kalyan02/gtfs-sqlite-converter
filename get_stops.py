import os, csv, re, difflib, math, sys, time, json, sqlite3, plistlib
from pprint import pprint 

reload(sys)
sys.setdefaultencoding('utf-8')


def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

db_name = 'gvb.db'
dbconn = sqlite3.connect(db_name)
dbconn.text_factory = str
dbconn.row_factory = dict_factory
dbcursor = dbconn.cursor()


def _get_all_top_trips():
	sql = """
		SELECT
			t.trip_id,
			t.shape_id,
			t.route_id as route_id,
			st.stop_id,
			count(*) AS cnt
		FROM trips t
		LEFT JOIN stop_times st
			ON st.trip_id = t.trip_id
		--WHERE t.route_id=r.route_id
		GROUP BY st.trip_id
		--GROUP BY t.route_id
		ORDER BY cnt DESC
		LIMIT 10
	"""

	lst = dbcursor.execute(sql)
	trips = lst.fetchall()

	pprint( trips )
	# sys.exit(-1)
	# return lst.fetchone()

def _get_top_trip(route_id):
	sql = """
	SELECT
		t.trip_id,
		t.shape_id,
		count(*) AS cnt
	FROM trips t
	LEFT JOIN stop_times st
		ON st.trip_id = t.trip_id
	WHERE t.route_id='%s'
	GROUP BY st.trip_id
	ORDER BY cnt DESC;
	"""

	lst = dbcursor.execute(sql % route_id)

	# pprint( lst.fetchall() )
	# sys.exit(-1)
	return lst.fetchone()


def _get_all_stops():
	sql = """
	SELECT 
		*
	FROM stops s
	"""
	lst = dbcursor.execute(sql)
	stops = lst.fetchall()

	stops_hash = { stop['stop_id'] : stop for stop in stops }
	#stops.sort(key=lambda x:x['stop_sequence'])
	return stops_hash

def _get_trip_stops(trip_id):
	sql = """
	SELECT 
		st.stop_id,
		st.stop_sequence,
		s.stop_lat,
		s.stop_lon,
		s.stop_name,
		s.parent_station as parent_id
	FROM stop_times st
	LEFT JOIN stops s
		ON s.stop_id = st.stop_id
	WHERE st.trip_id=?
	"""
	lst = dbcursor.execute(sql,(trip_id,))
	stops = lst.fetchall()
	stops.sort(key=lambda x:x['stop_sequence'])
	return stops

"""
	This method returns the stop lat/lon replaced with the parent's lat-lon
	and also adds the parent_id for easy retrieval or something like that!
"""
def _get_trip_stops_real(trip_id):
	if not hasattr(_get_trip_stops_real,'_all_stops'):
		_get_trip_stops_real._all_stops = _get_all_stops()

	_all_stops = _get_trip_stops_real._all_stops
	_trip_stops = _get_trip_stops(trip_id)

	# fetch the actual stop
	# and replace the lat, lon & the name to parent one
	for each_stop in _trip_stops:
		actual_stop_id = each_stop['parent_id']
		if actual_stop_id and len(actual_stop_id) > 0:
			actual_stop = _all_stops[ actual_stop_id ]
			# copy values from the parent to the stop for data file purposes
			each_stop['stop_lat'] = actual_stop['stop_lat']
			each_stop['stop_lon'] = actual_stop['stop_lon']
			each_stop['stop_name'] = actual_stop['stop_name']

	return _trip_stops

def _get_shape(shape_id):
	sql = """
	SELECT
		s.shape_pt_lat AS lat,
		s.shape_pt_lon AS lon,
		s.shape_pt_sequence,
		s.shape_dist_traveled AS dist
	FROM 
		shapes s
	WHERE
		s.shape_id = ? 
	"""

	lst = dbcursor.execute(sql,(shape_id,))
	shapepts = lst.fetchall()
	shapepts.sort(key=lambda x: x['shape_pt_sequence'])
	return shapepts
	pass

def _get_routes():
	sql = """
	SELECT 
		route_id,
		route_short_name AS short_name,
		route_long_name AS long_name 
	FROM routes
	"""
	lst = dbcursor.execute(sql)
	routes = lst.fetchall()
	routes.sort( key=lambda x: int(x['short_name']) )
	return routes

def _write_to_file(fname,content):
	if not os.path.exists(os.path.dirname(fname)):
		os.makedirs(os.path.dirname(fname))
	fh = open(fname,'w')
	fh.write(content)
	fh.close()

def _write_json(fname,obj):
	_write_to_file(fname,json.dumps(obj,indent=4))

def _write_plist(fname,obj):
	plistlib.writePlist(obj,fname)

# print _get_all_top_trips()
# sys.exit(-1)

if __name__ == '__main__':
	allroutes  = _get_routes()
	allstops = _get_all_stops()
	stop_to_parent_map = { e['stop_id'] : e['parent_station'] for e in allstops.values() if len(e['parent_station']) > 0 }

	_write_json( 'json/routes.json', allroutes )

	stop_routes_map = {}

	# for each route
	for i, route in enumerate(allroutes):
		route_id = route['route_id']
		print '%3d' % i, route_id

		# get route_id -> trip_id -> all stops
		trip = _get_top_trip(route_id)
		trip_id = trip['trip_id']
		trip_stops = _get_trip_stops_real(trip_id)

		for each_trip_stop in trip_stops:
			each_trip_stop_id = each_trip_stop['stop_id']
			if not stop_routes_map.has_key(each_trip_stop_id):
				stop_routes_map[ each_trip_stop_id ] = []

			stop_routes_map[ each_trip_stop_id ].append( route_id )


		# pprint(stop_routes_map)
		# sys.exit(-1)

		shape_id = trip['shape_id']
		trip_shape = _get_shape(shape_id)

		trip_shape_min = [ [e['lat'],e['lon']] for e in trip_shape ]

		route_fname = route_id.replace('|','_')
		_write_json( 'json/stops/%s.json' % route_fname, trip_stops )
		_write_json( 'json/shapes/%s.json' % route_fname, trip_shape_min )

	_write_json('json/stop_routes_map.json', stop_routes_map )
	_write_plist('json/stop_routes_map.plist', stop_routes_map )