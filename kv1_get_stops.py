import plistlib, sys
from pprint import pprint as pp

stop_coord_files = ['kv1_gvb/gvbhaltes.tsv'] #,'kv1_cxx/cxxhaltes.tsv']
stop_coords_map = {}
for each_service in stop_coord_files:
	fh = open(each_service,'r')
	lines = fh.readlines()
	del lines[0]
	lines = map( lambda x: x.split('|'), lines )
	# print lines[0]

	stop_coords_map = {
		item[1] : ( float(item[2]), float(item[3].strip()) )
		for item in lines
	}


	# try:
	print 'Waterlooplein', stop_coords_map['Waterlooplein']
	print 'Muiderpoortstation', stop_coords_map['Muiderpoortstation']
	# except Exception, e:
	# 	print 'SHIT', e, e.message
	# 	# raise
	# 	sys.exit(-1)

	# print stop_coords_map.keys()


user_stops_files = ['kv1_gvb/USRSTOPXXX.tmi'] #,'kv1_cxx/USRSTOP.TMI']
for each_file in user_stops_files:
	fh = open(each_file,'r')
	while True:
		try:
			line = fh.readline()
			if not line:
				print 'exit'
				break

			if 'Amsterdam'.lower() in line.lower():
				# print 'test', line
				split = line.split('|')
				info = {
					'service' : split[3],
					'stop_id' : split[4],
					'stop_name' : split[9],
					'stop_town' : split[10]

				}

				if info['service'] == 'GVB':
					info['name'] = split[9]
				if info['service'] == 'CXX':
					info['name'] = split[9].split(',',1)[1].strip()

				
				if not stop_coords_map.has_key( info['name'] ):
					print 'ERR   :(%s)' % info['name']
				else:
					print 'OK    :(%s)' % info['name']
				# print 'TEST :', stop_coords_map['Muiderpoortstation']


				# pp( info )
				# break
				# sys.exit(-1)
		except:
			raise
		pass
	sys.exit(-1)