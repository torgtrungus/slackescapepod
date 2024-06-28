import json
from tqdm import tqdm
import time # for debug




def import_users(filename, debug=False):
	f = open(filename, encoding="utf8")
	
	# returns JSON object as  dict
	data = json.load(f)
	


	# we want the id, name, real name


	users = {}

	pbar = tqdm(range(len(data)), desc='importing users') # progress bar

	for user in data:
		
		uid = user['id']
		profile = user['profile']

		real_name = ''
		if 'real_name' in user:
			real_name = user['real_name']
		else:
			# no real name? use display name instead
			if 'display_name' in profile:
				real_name = profile['display_name']

		display_name = ''
		if 'display_name' in profile:
			display_name = profile['display_name']

		# some people have no nickname, default to their 'real name'
		name = display_name
		if name == '':
			name = real_name

		if display_name == '': # default empty nickname to real name, because thats what we will show.
			display_name = real_name
		

		if debug:
			print('found user %s : \'%s\' : %s' % (real_name, display_name, uid))

		for k,v in user.items():
			#print('%s: %s' %(k,v))
			pass

		users[uid] = {
			'profile':profile,
			'real_name':real_name,
			'display_name':display_name,
			'name':name
		}	

		if 'USLACKBOT' not in users:
			# add slackbot as a double for now
			users['USLACKBOT'] = {
				'profile':None,
				'real_name':'Slackbot',
				'display_name':'Slackbot',
				'name':'Slackbot'
			}


		pbar.update(1)
		pbar.set_description(display_name)
		#time.sleep(1)
	pbar.set_description('User Import Complete')

	#print(users)
	return users
