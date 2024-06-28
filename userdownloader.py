import requests
#import pathlib # todo: have pathlib make the correct dirs for OS agnosticness
import os
import shutil


def download_users(users, output_dir):

	return_dict = {}
	# prepare destination dir
	export_root = output_dir
	avatars_dir = os.path.join(export_root, '.avatars')
	print('creating ' + avatars_dir)
	try:
		print('...creating avatars directory...')
		os.mkdir(avatars_dir)
	except FileExistsError:
		print('...directory already exists.')




	for uid in users:
		print('-------------\n\tworking on user ' + uid + '...')
		user = users[uid] # extract user dict from users using its key

		# create user dir
		user_dir = os.path.join(avatars_dir, uid)

		
		try:
			print('... creating ' + user_dir)
			os.mkdir(user_dir)
		except FileExistsError:
			print('...directory already exists.')

		
		if uid == 'USLACKBOT':
			cwd = os.getcwd()
		
			slackbot_av_path = os.path.join('assets','USLACKBOT-48.png')
			slackbot_av_path = os.path.join(cwd,slackbot_av_path)

			images_to_generate = [
				'image_original',
				'image_24',
				'image_32',
				'image_48',
				'image_72',
				'image_192',
				'image_512',
				'image_1024'
			]

			slackbot_av_dict = {}
			for image_name in images_to_generate:

				slackbot_av_dest_path = os.path.join(user_dir, image_name + '.png')

				slackbot_relative_av_path = '../.avatars/USLACKBOT/' + image_name + '.png'

				print('... copying slackbot avatar to ' + slackbot_av_dest_path)
				shutil.copy(slackbot_av_path, slackbot_av_dest_path)

				slackbot_av_dict[image_name] = slackbot_relative_av_path


			return_dict[uid] = slackbot_av_dict # store paths to avs


			continue

		# download the original image, and the 24px, 48 px, 192px and 1024px
		# store them in .avatars under their normalized name (which removes formatting chars)

		image_urls = []


		images_found = 0

		search_for_images = [
			'image_original',
			'image_24',
			'image_32',
			'image_48',
			'image_72',
			'image_192',
			'image_512',
			'image_1024'
		]

		largest_found = ''
		duplicate_images = [] # we will use this to find which images we need to 'duplicate' (missing 1024? just point the 1024 size to the largest image we DID find)

		for image_source in search_for_images:
			if image_source in user['profile']:
				images_found += 1
				largest_found = image_source
				image_urls.append((user['profile'][image_source].replace('\\',''),image_source))
			else:
				duplicate_images.append(image_source)

		#print('duplicate_images')
		#print(duplicate_images)


		destinations = []
		return_dict[uid] = {}

		for url, image_source in image_urls:

			# extract filename
			url_split = url.split('/')
			extension = url.split('.')[-1]
			#filename = url_split[-1] # no longer reliable, rename it to the source name
			filename = image_source + '.' + extension

			destination = os.path.join(user_dir, filename)
			relative_destination = '../.avatars/' + uid + '/' + filename
			
			destinations.append(relative_destination) # only give relative destination

			return_dict[uid][image_source] = relative_destination

			if os.path.exists(destination):
				print(filename + ' already exists, skipping...')
			else:
				print('\tdownloading ' + url)
				response = requests.get(url)
				#print(destination)
				#print('user dir: ' + user_dir)

				try:
					print('...writing to ' + destination)
					open(destination, "wb").write(response.content) # write binary
				except FileExistsError:
					print('...file already exists. continuing...')

					
				

		# some images may not have been found, so fake them by using the largest image we found
		for image_source in duplicate_images:
			return_dict[uid][image_source] = largest_found


		# changes accounts for the user not having some avatars. this assumed everyone had each avatar size
		# return_dict[uid] = {
		# 	'image_original': destinations[0],
		# 	'image_24' : destinations[1],
		# 	'image_48' : destinations[2],
		# 	'image_192' : destinations[3],
		# 	'image_1024' : destinations[4],
		# }

	return return_dict # has avatar locations

	