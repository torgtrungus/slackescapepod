import json
import os
import imagedownloader
from colorama import init, Fore, Back, Style

color_out = True

def disable_color():
	global color_out
	color_out = False


def import_posts(path_to_import, day_name, channel, output_dir, debug=False):
	

	#print(path_to_import)
	#print(day_name)
	#print(channel_dir)


	f = open(path_to_import, encoding="utf8")

	created_folder = False
	
	data = json.load(f)
	
	posts = []

	uploads_tuple = None

	for post in data:
		ptype = post['type']
		if ptype != 'message': # are any of these not messages?
			print('non message found:')
			print(post)
			exit(2)


		if debug: print(post)

		is_comment = False
		if 'subtype' in post:
			if post['subtype'] == 'file_comment':
				is_comment = True
				post['user'] = post['comment']['user']

		if debug: print('found post: %s , user: %s , time: %s' % (post['text'], post['user'], post['ts']))

		if 'files' in post:
			if debug: print('found upload(s)...')
			#print(post)

			if not created_folder: # create day image dir
				
				channel_dir = os.path.join(output_dir, channel)
				day_dir = os.path.join(channel_dir, day_name)
				
				try:
					print('\t...creating ' + day_dir)
					os.mkdir(day_dir)
					created_folder = True
				except FileExistsError:
					if color_out:
						print(Fore.YELLOW + '\t\t...directory already exists.' + Style.RESET_ALL)
					else:
						print('\t\t...directory already exists.')
					created_folder = True

			#imagedownloader.disable_color()
			uploads_tuple = imagedownloader.download_images(post, day_name, channel_dir, debug=debug)
		else:
			uploads_tuple = None



		# for k,v in post.items():
		# 	#print('%s: %s' %(k,v))
		# 	pass
	#	print('-------------')
	#	print(post)
	#	print(type(post))
		posts.append((post,uploads_tuple)) # posts is full of tuples: post and file locations if any
	#z = ''
	#print('------------------------ posts')
	#print(posts)
	#input(z)
	return posts
