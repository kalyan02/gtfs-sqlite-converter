from get_stops import _get_all_stops
from pprint import pprint as pp
import plistlib, sys

reload(sys)
sys.setdefaultencoding('utf-8')

allstops = _get_all_stops()

allstops = { i : e for i, e in allstops.items() }
# print len(allstops)
# sys.exit(-1)

# stop_to_parent_map = { e['stop_id'] : e['parent_station'] for e in allstops.values() }
# parent_to_stop_map = {}
# for stop_id, parent_id in stop_to_parent_map.items():
# 	stops_for_parent = parent_to_stop_map.get(parent_id,[])
# 	stops_for_parent.append( stop_id )
# 	parent_to_stop_map[parent_id] = stops_for_parent

# pp(parent_to_stop_map[''])
# print len(parent_to_stop_map[''])
# print len(parent_to_stop_map)

for stopinfo in allstops.values():
	sns = stopinfo['stop_name'].split(",",1)	# split
	sns = map( lambda x: x.strip(), sns )		# strip
	sns = sns[::-1]								# reverse
	stopinfo['stop_name'] = ", ".join( sns )	# join

	pass

plistlib.writePlist(allstops,'amsterdam_now/stops.plist')
plistlib.writePlist(allstops,'/Users/kalyan/Dropbox/Projects/Labs/RoutingApps/AmsterdamNow/AmsterdamNow/stops.plist')

