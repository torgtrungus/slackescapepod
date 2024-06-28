import json




def import_channels(filename):
	f = open(filename, encoding="utf8")
	
	data = json.load(f)
	
	channels = {}

	for channel in data:
		cid = channel['id']
		name = channel['name']
		#creator = channel['creator']

		print('found channel: %s , topic: %s , purpose: %s' % (name, channel['topic']['value'], channel['purpose']['value']))

		for k,v in channel.items():
			#print('%s: %s' %(k,v))
			pass

		channels[name] = channel

	#print(channels)
	return channels
