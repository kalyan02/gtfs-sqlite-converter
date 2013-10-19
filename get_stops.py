import os, csv, re, difflib, math, sys, time, json, sqlite3

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
	return lst.fetchone()


def _get_stops(trip_id):
	sql = """
	SELECT 
		st.stop_id,
		st.stop_sequence,
		s.stop_lat,
		s.stop_lon,
		s.stop_name
	FROM stop_times st
	LEFT JOIN stops s
		ON s.stop_id = st.stop_id
	WHERE st.trip_id=?
	"""
	lst = dbcursor.execute(sql,(trip_id,))
	stops = lst.fetchall()
	stops.sort(key=lambda x:x['stop_sequence'])
	return stops

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

allroutes  = _get_routes()


_write_json( 'json/routes.json', allroutes )
for i, route in enumerate(allroutes):
	route_id = route['route_id']
	print '%3d' % i, route_id

	trip = _get_top_trip(route_id)
	trip_id = trip['trip_id']
	shape_id = trip['shape_id']
	trip_stops = _get_stops(trip_id)
	trip_shape = _get_shape(shape_id)

	trip_shape_min = [ [e['lat'],e['lon']] for e in trip_shape ]

	route_fname = route_id.replace('|','_')
	_write_json( 'json/stops/%s.json' % route_fname, trip_stops )
	_write_json( 'json/shapes/%s.json' % route_fname, trip_shape_min )
