import os, csv, re, difflib, math, sys, time, json, sqlite3
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db",dest="db")
parser.add_option("-s", "--src", dest="src")
kwargs, inputs = parser.parse_args()

db_name = kwargs.db #'gvb.db'
input_directory = kwargs.src #'./gtfs_amsterdam/'

fields_type_map = {
 'agency_id': 'TEXT',
 'agency_lang': 'TEXT',
 'agency_name': 'TEXT',
 'agency_phone': 'TEXT',
 'agency_timezone': 'TEXT',
 'agency_url': 'TEXT',
 'arrival_time': 'TEXT',
 'block_id': 'TEXT',
 'date': 'TEXT',
 'departure_time': 'TEXT',
 'direction_id': 'TEXT',
 'drop_off_type': 'INTEGER',
 'end_date': 'TEXT',
 'exception_type': 'INTEGER',
 'friday': 'INTEGER',
 'location_type': 'INTEGER',
 'monday': 'INTEGER',
 'parent_station': 'INTEGER',
 'pickup_type': 'INTEGER',
 'route_color': 'TEXT',
 'route_desc': 'TEXT',
 'route_id': 'TEXT',
 'route_long_name': 'TEXT',
 'route_short_name': 'TEXT',
 'route_text_color': 'TEXT',
 'route_type': 'INTEGER',
 'route_url': 'TEXT',
 'saturday': 'INTEGER',
 'service_id': 'TEXT',
 'shape_dist_traveled': 'REAL',
 'shape_id': 'TEXT',
 'shape_pt_lat': 'REAL',
 'shape_pt_lon': 'REAL',
 'shape_pt_sequence': 'INTEGER',
 'start_date': 'TEXT',
 'stop_code': 'INTEGER',
 'stop_desc': 'TEXT',
 'stop_headsign': 'TEXT',
 'stop_id': 'TEXT',
 'stop_lat': 'REAL',
 'stop_lon': 'REAL',
 'stop_name': 'TEXT',
 'stop_sequence': 'INTEGER',
 'stop_url': 'TEXT',
 'sunday': 'INTEGER',
 'thursday': 'INTEGER',
 'trip_headsign': 'TEXT',
 'trip_id': 'TEXT',
 'tuesday': 'INTEGER',
 'wednesday': 'INTEGER',
 'zone_id': 'TEXT',

 'trip_short_name' : 'TEXT',
 'timepoint' : 'INTEGER',
 'trip_bikes_allowed' : 'INTEGER',
 'wheelchair_accessible' : 'INTEGER',
}

index_fields = [
 'trip_id',
 'stop_id',
 'shape_id',
 'route_id',
 'service_id',
 'stop_sequence',
 'shape_pt_sequence'
]

default_field_type = 'TEXT'

files = [
 'agency.txt',
 'calendar_dates.txt',
 'feed_info.txt',
 'routes.txt',
 'shapes.txt',
 'stop_times.txt',
 'stops.txt',
 'trips.txt'
]

def get_field_type(f):
	global fields_type_map, default_field_type
	if not fields_type_map.has_key(f):
		return default_field_type
	else:
		return fields_type_map[f]




if os.path.exists(db_name):
	os.unlink(db_name)

dbconn = sqlite3.connect(db_name)
dbconn.text_factory = str
dbcursor = dbconn.cursor()

input_directory = input_directory.strip().strip('/')
if len(input_directory) == 0:
	input_directory = '.'

for each in files:
	each_file_name = '%s/%s' % (input_directory, each)

	fh = open(each_file_name,'r')
	reader = csv.reader( fh )
	fields = reader.next()
	table_name = os.path.basename(each).replace('.txt','')

	##### CREATE TABLE
	fields_list = []
	for each in fields:
		fsql = '%s %s' % (each, get_field_type(each))
		fields_list.append(fsql)

	fields_list = ",\n".join( fields_list )

	create_sql = "CREATE TABLE %s( %s );" % (table_name, fields_list)
	print 'creating %s' % table_name
	dbcursor.execute( create_sql )

	##### CREATE INDEXES
	for index_field in set(fields) & set(index_fields):
		index_sql = 'CREATE INDEX %s_%s ON %s(%s)' % (table_name,index_field,table_name,index_field)
		dbcursor.execute(index_sql)

	##### INSERT DATA
	i = 0
	try:
		while True:
			i += 1
			row = reader.next()
			insert_sql = 'INSERT INTO %s VALUES(%s)' % ( table_name,",".join(['?']*len(row)) )
			dbcursor.execute(insert_sql,row)
	except Exception, e:
		print "inserted %d rows\n" % i
		pass

dbconn.commit()
dbconn.close()

