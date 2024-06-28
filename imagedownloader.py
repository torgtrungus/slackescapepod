import requests
#import pathlib # todo: have pathlib make the correct dirs for OS agnosticness
import os
from colorama import init, Fore, Back, Style
from tqdm import tqdm # for progress bar if we know the file size (we don't know the thumbnail sizes)
#from pbar import .......

skip_count = 0

color = True

def disable_color():
	global color
	color = False

def do_download(url, saving_strings, file_size=None, is_thumb=False, verbose=False): # if we know the file size, use a progress bar

	global skip_count
	global color

	file_id, day_img_dir, day_name = saving_strings # put the file in the right place

	# extract filename to save correctly
	url_split = url.split('/')
	filename = url_split[-1]
	filename = filename.split('?')[0] # remove the token from the end of the filename
	
	saved_filename = file_id + '_' + filename # make unique with file_id
	destination = os.path.join(day_img_dir, saved_filename)

	relative_destination = day_name + '/' + saved_filename

	if os.path.exists(destination):
		if verbose:
			if color: print(Fore.YELLOW, end='') 
			print('\t...' + filename + ' already exists, skipping...')
			if color: print(Style.RESET_ALL, end='')	
		
		skip_count += 1
	
	else: # file does not exist yet


		# block of text output
		print('\tdownloading ', end='')
		if is_thumb:
			print('thumbnail ', end='')
		if color: print(Fore.BLUE + Style.BRIGHT, end='')
		print(filename)
		if color: print(Style.RESET_ALL, end='')

		response = requests.get(url, stream=True) # need stream to do progressbar (if applicable)

		total_size_bytes = file_size # if we know the file_size, it is the original file. otherwise it is a thumb (this isn't really necessary, but we can add a 'do not download thumbnails option' later) # todo: add 'no thumbnails' option and just use originals

		block_size = 1024 # 1 KB (KiB), not 1 kB.

		try:
			#if color: print(Fore.CYAN + Style.BRIGHT, end='')
			#print('\t...writing to ' + destination)
			#if color: print(Style.RESET_ALL, end='')

			pbar = ''
			bar_color = 'green'

			if not color:
				bar_color = None


			# do we need a specific progress bar? If we don't know the file_size we need to guess.
			# 3 cases: we knew it from the post metadata, we get it from the response header, or we don't get it from the response header
			if file_size is None: 

				total_size_bytes = int(response.headers.get('content-length', 0)) # get the download's filesize from the request instead of from the post data

				if total_size_bytes <= 0:
					if color:
						print(Fore.RED + 'ERROR: no content-length in response header. Unknown Filesize...' + Style.RESET_ALL)
					else:
						print('ERROR: no content-length in response header. Unknown Filesize...')

					# progress bar with no known end:
					pbar = tqdm(unit='KB',
						unit_scale=True,
						desc=filename,
						colour=bar_color,
						leave=False)

				else:
					# looks ok, we found out a filesize from the header
					pbar = tqdm(total=total_size_bytes,
						unit='KB',
						unit_scale=True,
						desc=filename,
						colour=bar_color,
						leave=False)

			else:
				# we already knew the filesize

				pbar = tqdm(total=file_size,
					unit='KB',
					unit_scale=True,
					desc=filename,
					colour=bar_color,
					leave=False)
			


			with open(destination, "wb") as file:
				for data in response.iter_content(block_size):
					pbar.update(len(data))
					file.write(data) # write binary

			pbar.close()

			#print("pbar.n:") # show total bytes
			#print(pbar.n)

			# original way, before using progress bar: open(destination, "wb").write(response.content) # write binary

		except FileExistsError: # shouldn't happen, but let's be safe and prevent a crash in case it does for whatever strange reason

			if color: print(Fore.YELLOW, end='') 
			print('...file already exists. continuing...')
			if color: print(Style.RESET_ALL, end='')

	return relative_destination, filename


def download_images(post, day_name, channel_dir, debug=False, verbose=False):

	global skip_count

	#print(post)
	#print(day_name)
	#print(output_dir)

	day_img_dir = os.path.join(channel_dir, day_name)


	#exit(1)

	# prepare destination dir (already has been stripped of extension)

	# already handled in postsimporter.py
	# day_img_dir = os.path.join(channel_dir, day_name)
	# try:
	# 	#print('creating ' + day_img_dir + ' ...')
	# 	os.mkdir(day_img_dir)
	# except FileExistsError:
	# 	#print('...directory already exists.')


	return_vals = []
	skip_count = 0

	files = post['files']

	for file in files:

		file_id = file['id']
		file_mode = file['mode']
		if file_mode == 'tombstone':
			print('found deleted file, ignoring')
			continue

		file_type = ''
		if 'mimetype' in file:
			file_type = file['mimetype']
		else:
			file_type = 'unknown'

		file_size = ''
		if 'size' in file:
			file_size = file['size']
		else:
			file_size = 'unknown'

		title = ''
		if 'title' in file:
			title = file['title']
		else:
			title = 'unknown'

		if debug: print(file)

		if 'video' in file_type:

			print('-------------\n\tworking on video ' + file_id + '...')

			thumb_url = None
			if 'thumb_video' in file:
				thumb_url = file['thumb_video']
			url = file['url_private']

			saving_strings = (file_id, day_img_dir, day_name)

			print(saving_strings)
			#print('todo: fixme: need to implement download progressbar or whatever')
			#exit(1) # need to figure out if this changes


			thumb_relative_destination = ''
			thumb_size_for_return = None

			# download only if it exists
			relative_destination, filename = do_download(url, saving_strings, verbose=verbose)

			if thumb_url is not None:
				thumb_relative_destination, _ = do_download(thumb_url, saving_strings, is_thumb=True, verbose=verbose)
				thumb_size_for_return = 'thumb_720' # todo: figure out if this is going to mess stuff up down the line

			return_vals.append(
					(
					file_type,
					file_size,
					relative_destination,
					filename,
					thumb_relative_destination,
					thumb_size_for_return, # thumb_size
					title
					)
				)

		elif 'image' in file_type:
			print('-------------\n\tworking on image ' + file_id + '...')


			# download the original image, and the 720px thumb (or biggest thumb that exists)
			# we need to return the thumb size we get

			orig_w = 0
			thumb_size = 'url_private' # default to using url_private if didn't have a width
			image_urls = []

			if 'original_w' in file and 'original_h' in file:
				orig_w = file['original_w']
				orig_h = file['original_h']

				thumb_size = 'thumb_720' # goal is to get 720 thumb. if smaller, use next biggest

				if orig_w <= 720 or 'thumb_720' not in file: # sometimes there is no thumb at 720 if it matches up to 720 in the original file dimensions
					thumb_size = 'thumb_480'
					if orig_w <= 480:
						thumb_size = 'thumb_360'
						if orig_w <= 360:
							thumb_size = 'thumb_80'
							if orig_w <= 80:
								thumb_size = 'thumb_64'
								if orig_w <= 64:
									thumb_size = 'url_private' # too small just use original as thumbnail

			if debug: print('orig_w',orig_w)
			if debug: print('thumb_size',thumb_size)
			
			fullsize_url = file['url_private'].replace('\\','')
			thumb_url = file[thumb_size].replace('\\','')




			if thumb_size in file:
				image_urls.append((fullsize_url, thumb_url, file_type, file_size, file_id, title))
			else:
				if debug:print('found a file without a thumb!')
				print(file)
				exit(1)
			#print(image_urls)



			for url_tup in image_urls:

				fullsize_url, thumb_url, file_type, file_size, file_id, title = url_tup

				saving_strings = (file_id, day_img_dir, day_name)

				relative_destination, filename = do_download(fullsize_url, saving_strings, file_size=file_size, verbose=verbose) # download original
				thumb_relative_destination, _ = do_download(thumb_url, saving_strings, is_thumb=True, verbose=verbose) # download thumbnail

				return_vals.append(
						(
						file_type,
						file_size,
						relative_destination,
						filename,
						thumb_relative_destination,
						thumb_size,
						title
						)
					)
					
			pass

	if skip_count > 0:
		if color:
			print(Fore.YELLOW + '\tskipped %d downloads' % (skip_count) + Style.RESET_ALL)
		else:
			print('\tskipped %d downloads' % (skip_count))
	return return_vals
	