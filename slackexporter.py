#________________________________________________________        
# ________________________________________________________       
#  _____/\\\____________________________________/\\\\\\\\__      
#   __/\\\\\\\\\\\_____/\\\\\_____/\\/\\\\\\\___/\\\////\\\_     
#    _\////\\\////____/\\\///\\\__\/\\\/////\\\_\//\\\\\\\\\_    
#     ____\/\\\_______/\\\__\//\\\_\/\\\___\///___\///////\\\_   
#      ____\/\\\_/\\__\//\\\__/\\\__\/\\\__________/\\_____\\\_  
#       ____\//\\\\\____\///\\\\\/___\/\\\_________\//\\\\\\\\__ 
#        _____\/////_______\/////_____\///___________\////////___
#
#                          who cares  2 0 2 4 
#                            
#
#                 https://github.com/torgtrungus/slackescapepod


import userimporter
import userdownloader
import channelsimporter
import postsimporter
import emojidownloader
import json
import math
from os import walk, getcwd, path, mkdir, sep
import os # ffs
from colorama import init, Fore, Back, Style
init()
import shutil
from tqdm import tqdm
from time import sleep # for debug
from datetime import datetime
from zipfile import ZipFile 


# todo: accept arguments

debug = False
color = True # color output
ignore_errors = False # todo: have this be an argument



def exit_with_error(msg):
	global ignore_errors
	global color

	msg_chunk = 'Msg: "' + msg + '" ' 
	if len(msg) == 0:
		msg_chunk = ''

	if not ignore_errors:
		if color:
			print(Fore.RED + '[Exited due to an error.' + msg_chunk + ' To ignore errors use the -i argument. This may lead to formatting issues.]' + Style.RESET_ALL)
		else:
			print('[Exited due to an error.' + msg_chunk + ' To ignore errors use the -i argument. This may lead to formatting issues.]')

		exit(1)

	else:
		if color:
			print(Fore.RED + '[Ignoring error.]' + Style.RESET_ALL)
		else:
			print('[Ignoring error.]')


print('[_______ EscapePod : a Slack Exporter _______]')


print('Paste Slack subdomain :')

subdomain = input()

if len(subdomain) == 0:
	exit_with_error('Subdomain cannot be empty')


print('Paste emoji token (press enter to skip):')

emoji_token = input()



print('Paste absolute path to zip:')

zip_path = input()

# secretly clean quotes to help out lazy people
zip_path_quote_cleaner = zip_path.split('"')

if len(zip_path_quote_cleaner) == 3:
	# quotes detected (i hope)
	zip_path = zip_path_quote_cleaner[1] # take the middle one only

#verify zip exists

if not path.exists(zip_path):
	exit_with_error(' Zip file not found. Exiting...')

# extract name of zip file

zip_path_components = zip_path.split(sep)

#print(zip_path_components[-1]) # zip
#print(zip_path_components[:-1]) # dir of zip

zip_name = zip_path_components[-1].split('.')[0]

drive_path = path.splitdrive(zip_path_components[0])[0] # windows will have the drive letter fall off if we dont do this

working_dir = path.join('') # build path of dir of zip
for path_component in zip_path_components[0:-1]:
	#print('path component:', path_component)
	working_dir = path.join(working_dir, path_component)

working_dir = path.join(drive_path, os.sep, working_dir) # add the drive letter back in


unzip_dir = path.join(working_dir, zip_name)


output_dir = path.join(working_dir, zip_name + ' EscapePod')

# create unzip dir
if path.exists(unzip_dir):
	pass
else:
	print('creating directory :\n', unzip_dir )
	mkdir(unzip_dir)


with ZipFile(zip_path, 'r') as zipfile:
	zipfile.extractall(path = unzip_dir) 


# create output dir
if path.exists(output_dir):
	pass
else:
	print('creating directory :\n', unzip_dir )
	mkdir(output_dir)


#print('length: ', len(emoji_token))
# if emoji_token len is 0 it wont try to download emojis

working_dir = unzip_dir # older versions used working_dir instead of unzip dir so this is a quick fix for the rest of the code
  






def slackbot_emoji_parser(string):

	global emojis # for custom emojis
	global emoji_html_map # for standard emojis

	# go through string and turn emoji codes into emoji html

	# find start of emoji
	start_i = string.find(':') + 1
	end_i = string.find(':', start_i + 1)

	if start_i == -1 or end_i == -1:
		if color:
			print(Fore.YELLOW + 'no emoji found, keeping slackbot post as is' + Style.RESET_ALL)
		else:
			print('no emoji found, keeping slackbot post as is')


		return string

	emoji_name = string[start_i:end_i]

	#print('found possible emoji in string: ' + string + 'at indices %d through %d: ' % (start_i, end_i-1) + emoji_name)

	preceding_string = ''

	if start_i-1 > 0:
		preceding_string = string[:start_i]

	remaining_string = ''

	reached_end_of_string = end_i + 1 == len(string) # are we at the end of the string?

	if not reached_end_of_string:
		remaining_string = string[end_i+1:]



	result = preceding_string
	
	if emoji_name in emojis: # custom emoji
		result += '<img class="emoji_in_text" src="' + emojis[emoji_name] + '">'
	else: # standard emoji
		if emoji_name in emoji_html_map:
			unicode_emoji = emoji_html_map[emoji_name]
		else:
			unicode_emoji = '&#x1F533;' # default for missing emoji? white square
		result += '<span class="text_emoji">' + unified_to_html(unicode_emoji) + '</span>'

	if reached_end_of_string:
		return result
	else:
		return result + slackbot_emoji_parser(remaining_string)
	

def unified_to_html(string):
	return '&#x' + string.replace('-', ';&#x') + ';'

def clean_slashes(string):
	cleaned = string.replace('\n','<br>')
	cleaned = cleaned.replace('\\/','/')
	return cleaned


def rich_text_list_to_html(rt_list):
	html = ''
	style = rt_list['style']

	if style == 'ordered':
		ltype = 'ol'
		html += '<' + ltype + ' class="ordered_list list">'
	else:
		ltype = 'ul'
		html += '<' + ltype + ' class="unordered_list list">'

	for element in rt_list['elements']:

		t = element['type']

		if t == 'rich_text_section':
			html += '<li>' + rich_text_section_to_html(element) + '</li>'

	html += '</' + ltype + '>'

	return html

def rich_text_quote_to_html(rt_element):
	html = ''
	for element in rt_element['elements']:
		text = clean_slashes(element['text'])
		html += '<div class="blockquote">' + text + '</div>'

	return html

def rich_text_preformatted_to_html(rt_element):
	html = '<div class="codeml">'
	for element in rt_element['elements']:
		text = clean_slashes(element['text'])
		html += text

	html += '</div>'
	return html


def rich_text_section_to_html(rt_section):

	global emojis # req for custom emojis

	html = ''

	for element in rt_section['elements']:

		t = element['type']
		text = ''

		# different results based on t (type)
		if t == 'text':

			text = clean_slashes(element['text'])
			text_html = text

			if 'style' in element:

				for key, val in element['style'].items(): # we can ignore vals with, (always true)

					if key == 'bold':
						text_html = '<b>' + text_html
						text_html += '</b>'
					elif key == 'italic':
						text_html = '<i>' + text_html
						text_html += '</i>'
					elif key == 'strike':
						text_html = '<s>' + text_html
						text_html += '</s>'
					elif key == 'code':
						text_html = '<span class="codesl">' + text_html + '</span>'
					elif key == 'unlink': # this is when a link has had the auto url removed
						text_html = text
					else:
						print('error! found unknown style:', key)
						print('in element:', element)
						exit_with_error()

			html += text_html

		elif t == 'link':

			url = element['url'].replace('\\/','/')

			if 'text' in element:
				text = clean_slashes(element['text'])
			else:
				text = url
				
			html += '<a class="rts_link" href="' + url +'">' + text + '</a>'

		elif t == 'emoji':

			emoji_name = element['name']

			if emoji_name in emojis: # custom emoji
				html += '<img class="emoji_in_text" src="' + emojis[emoji_name] + '">'
			else: # standard emoji
				if 'unicode' in element:
					html += '<span class="text_emoji">' + unified_to_html(element['unicode']) + '</span>'
				else:
					html += '<span class="text_emoji">' + '&#x1F533;' + '</span>' # default for missing emoji? white square 

		elif t == 'user':
			html += '@' + users[element['user_id']]['name'] # todo: add a link to user profile here

		elif t == 'channel':
			# i don't know what this was. it has no content. maybe it was @ing the channel?
			channel_id = element['channel_id']
			channel_name = ''
			#print('channels:')
			#print(channels)
			for channel in channels:
				channel_d = channels[channel]
				#print(channel_d)
				if channel_d['id'] == channel_id:
					channel_name = channel_d['name']
			
			html += '@' + channel_name
			#print('not sure what this is actually')
		else:
			print('error! found rich text section with an element that is not type:text/link/emoji/user!')
			print('rts_element:', element)
			#exit_with_error()

			# instead, we will just dump the element in case it is important to context
			html += 'unknown element type in post: ' + t


	# print('finished parsing rich text section...')
	# print('result:', html)

	return html

def blocks_to_html(blocks):

	html = ''



	for block in blocks:

		t = block['type']

		if t == 'rich_text':

			rt_elements = block['elements']

			for rt_element in rt_elements:

				t = rt_element['type']

				if t == 'rich_text_section':
					html += rich_text_section_to_html(rt_element)
				elif t == 'rich_text_list':
					html += rich_text_list_to_html(rt_element)
				elif t == 'rich_text_quote':
					html += rich_text_quote_to_html(rt_element)
				elif t == 'rich_text_preformatted':
					html += rich_text_preformatted_to_html(rt_element)
				else:
					print('error! found rich text block of unknown type!')
					print('type:',rt_element['type'])
					print('element:',rt_element)
					exit_with_error()

		elif t == 'image':

			print()
			pass

		elif t == 'context': # bot context at end
			pass


		#print (block)

	return html




users_file = path.join(unzip_dir, 'users.json')
channels_file = path.join(unzip_dir, 'channels.json')


if path.exists(output_dir):
	print('output_dir already exists... continuing...')
	pass
else:
	print('output_dir does not exist, creating...')
	mkdir(output_dir)



#print('importing users...')
users = userimporter.import_users(users_file)
#print('\t...user import done')

print('downloading avatars...')
avatars = userdownloader.download_users(users, output_dir)
print('\t...avatar downloads done')

print('importing channels...')
channels = channelsimporter.import_channels(channels_file)
print('\t...channel imports done')

if len(emoji_token) == 0:
	print('no token for emojis, skipping...')
else:
	#print('downloading emojis...')
	emojis = emojidownloader.download_emojis(token=emoji_token,output_dir=output_dir,subdomain=subdomain,debug=debug)
	#print('\t...emoji downloads done')
	#print(emojis)

print('preparing emoji html...')
f = open('emoji_name2unified.json', encoding="utf8")
emoji_html_map = json.load(f)

print('importing posts...')


# setup css assets
cwd = getcwd()
assets_path = path.join(cwd, 'assets')
assets_destination = path.join(output_dir, '.assets')
print('assets_path: ' + assets_path)
print('assets_destination: ' + assets_destination)


#if path.exists(assets_destination):
#	# delete it if it exists (we may need to update css)
#	shutil.rmtree(assets_destination)
#	#print(assets_destination + 'assets already exists, skipping...')
#else:
#	pass # todo: clean this logic up

if not path.exists(assets_destination):
	shutil.copytree(assets_path, assets_destination)


# these will be used at the end to update all the posts with threads.
threads_dict = {} # maps thread_ts to a dict of {'html': file it needs to go to. 'anchor':the link to open the thread on the right( todo: this needs to be figured out later)}
replies_dict = {} # maps the reply ts to a dict of {'post': the reply post, 'html': the reply date filename}, so we can correct for image urls




last_poster = ''
last_timestamp_i = 0

def generate_html_from_post(tup,channel_path,mode='normal',force_av=False, original_day=None):

	global debug

	post, uploads_tup = tup

	global last_poster
	global last_timestamp_i
	global threads_dict
	global replies_dict
	
	phtml = ''


	# these are used before building threads. use mode to tell if we are building threads/replies
	is_thread = False
	is_reply = False

	is_bot = 'bot_id' in post # handles things like app posts (giphy etc), but not able to handle everything

	if is_bot:
		print('found bot post')
		print (post) ############################################### << Just post the bot's text
		#exit(1)

	if debug:
		print ('generating html for post:', post['text'])
		print ('mode:', mode)
		print ('post', post)
	
	if 'reply_count' in post: # threads and replys have 'thread_ts' in them but only threads have 'reply_count'
		#print('found a thread. saving', post['thread_ts'], 'for later...')
		is_thread = True
		if mode == 'normal': # save for later
			threads_dict[post['thread_ts']] = {
				'html' : file.replace('json', 'html'),
				'anchor' : 'todo-maketheanchorwork',
				'tup' : tup, # has the post and the uploads_tuple (if necessary)
				'channel_path': channel_path # only need channel for thread (can't reply cross channel)
			} # 15xxxxxxxx.xxxxxx -> {'html':'2018-xx-xx.html', 'anchor':'todo-maketheanchorwork', 'post':post}

	if 'thread_ts' in post and is_thread == False:
		# must be a reply
		#print('found a reply.')

		is_reply = True
		if mode == 'normal': # save for later
			reply_tup = {
				'tup' : tup, # has the post and the uploads tuple
				'post': post,
				'html': file.replace('json', 'html')
			}
			replies_dict[post['ts']] = reply_tup # save reply for later when we build the threads
		

		# if 'subtype' is a key in the post, it is a broadcast 
		if 'subtype' in post:
			if debug: ('subtype:', post['subtype'])
			if post['subtype'] == 'thread_broadcast': # if broadcasting (posting reply to channel also)
				pass
			if debug: print(' not writing post because it is an unbroadcasted reply and we are in the main channel')
		else:
			if mode == 'normal':
				return '' # we don't write the reply unless mode='thread_reply'

	if debug:
		if is_thread: print ('is_thread') 
		if is_reply: print ('is_reply')


	# file comment support (pre-thread comments)

	is_comment = False
	is_titled_upload = False
	if 'subtype' in post:
		if post['subtype'] == 'file_comment':
			is_comment = True
			post['user'] = post['comment']['user']
	elif 'upload_reply_to' in post:
		is_comment = True
		is_titled_upload = True # in this case, we don't need to parse the 'text', just place it after the image thumb.


	
	# check if the last post was within 5 minutes by the same user. if so, no avatar.
	timestamp_i = int(float(post['ts'])) # need to cast to float since slack stores timestamp with high precision
	timestamp = datetime.fromtimestamp(timestamp_i) # utcfromtimestamp is not helpful. this defaults to the timezone of the person exporting.

	timestamp_string = ''

	if mode == 'thread_reply':
		# a reply has a diff timestamp: 'x days ago' originally, now 'x days later'

		reply_difference = float(post['ts']) - float(post['thread_ts'])

		if reply_difference/60/60 < 24: # less than 24 hours
			
			if reply_difference/60 < 60: # less than 60 minutes

				if reply_difference < 60 : # < 60 seconds
					secs_later = math.floor(reply_difference)
					timestamp_string = str(int(secs_later)) + ' seconds later'
				else:
					mins_later = math.floor(reply_difference/60)
					timestamp_string = str(int(mins_later)) + ' minutes later'
			else:
				# above an hour
				hours_later = math.floor(reply_difference/60/60)
				timestamp_string = str(int(hours_later)) + ' hours later'
		else:
			# reply happened days later
			days_later = hours_later = math.floor(reply_difference/60/60/24)
			timestamp_string = str(int(days_later)) + ' days later'

	elif mode == 'thread': # we assume this is the start of the thread

		#day = timestamp.strftime('%-d') # this throws an error...
		# ...so we can manually remove the preceding 0
		day = timestamp.strftime('%d')
		if len(day) > 1:
			if day[0] == '0':
				day = day[1]
		timestamp_string = timestamp.strftime('%b X \'%y at %I:%M %p')
		timestamp_string = timestamp_string.replace('X', day)

	else: # we are in a channel, not a thread
		timestamp_string = timestamp.strftime('%I:%M %p') # %Y-%m-%d %H:%M:%S # (%I uses non 24h, need p to see am pm)
	
	
	no_avatar = False

	if last_timestamp_i != 0:
		if 'user' in post:
			if timestamp_i - last_timestamp_i < 60 * 5 and last_poster == post['user']:
				# 60 * 5 = 5 minutes worth of seconds
				no_avatar = True
				#print('no avatar because,',last_timestamp_i,' and ',last_poster)
				if force_av: no_avatar = False



	# convert to text ---------

	# prepare post uploads html here
	upload_html = ''

	sender_name = ''
	if 'user' in post:
		if post['user'] in users:
			if 'name' in users[post['user']]:
				sender_name = users[post['user']]['name']

	if sender_name == '':
		if 'username' in post:
			sender_name = post['username']
		else:
			if 'username' in post:
				sender_name = post['username']
			else:
				sender_name = 'unknown'

	#if sender_name == '':
	#	sender_name = users[post['user']]['profile']['real_name']

	#print('\nmaking html from post with text:', post['text'],'\n')

	if uploads_tup != None and not is_titled_upload: # titled upload is an old format with an assignable title that appears above the image. if it is a titled upload, we would have already posted the image, so don't do it again here.
		#print('in post by ' + sender_name)
		#print('found %d uploads in post' % (len(uploads_tup)) )
		#print(uploads_tup)
		#print(post)
		#print('')
		for upload in uploads_tup:
			#print(upload)

			file_type, file_size, file_location, file_name, thumb_location, thumb_size, file_title = upload

			is_gif = False
			is_video = False

			video_types = ['.mp4', '.mov']

			if file_location[-4:].lower() == '.gif':
				is_gif = True
			elif file_location[-4:].lower() in video_types: # todo: add support for more media types
				is_video = True

			if mode == 'thread' or mode == 'thread_reply':
				#file_url_split = file_location.split('/')
				file_location = '../' + file_location
				thumb_location = '../' + thumb_location


			upload_html += '''
                <span class="filename">'''
			upload_html += file_title + '</span><br>'

			if is_gif:

				upload_html += '<a href="%s"><img src="%s" class="gif_embed"></a>' %(file_location, file_location) # no thumb for gifs

			elif is_video:

				upload_html += '<a href="%s">Media Link</a><br><video class="thumbnail_video" width="270" controls><source src="%s">Media not supported</video>' %(file_location, file_location) #thumb_location) # thumb location not needed for video

			else: # any other file type (for now we only support images) # todo: add support for attachments

				upload_html += '<a href="%s"><img src="%s" class="thumbnail" width="270"></a>' %(file_location, thumb_location)
				#upload_html += str(upload)


	# begin post html

	tombstone = False
	if 'user' in post:

		if 'subtype' in post and post['user'] == 'USLACKBOT':
				if post['subtype'] == 'tombstone':
					tombstone = True
	elif 'username' in post: # probably rafflebot or something, just use the 'username' of the bot as the 'user' of the post
		post['user'] = post['username']


	if no_avatar:
		phtml += '''    <div class="post noav">
        <div class="gutter_l">
            <div class="hidden_timestamp_container">
                <a class="timestamp_link">
                    <span class="timestamp">
                        '''
		# add timestamp
		phtml += timestamp_string

		phtml += '''
                    </span>
                </a>
            </div>
        </div>
        '''
	else: # there is an avatar



		if tombstone:
			# override slackbot icon with trashcan

			phtml += '''    <div class="post">
        <div class="gutter_l">
            <div class="av">
                <span class="av_icon_container">
	                <div class="tombstone_icon">
	                    <svg class="tombstone_svg" data-us8="true" viewBox="0 0 20 20" style="--s: 20px;">
	                        <g fill="none" stroke="currentColor" stroke-width="1.5">
	                            <path stroke-linejoin="round" d="M4.25 7.25h11.5v9a1.5 1.5 0 0 1-1.5 1.5h-8.5a1.5 1.5 0 0 1-1.5-1.5v-9Zm-1.5-1.5a1.5 1.5 0 0 1 1.5-1.5h11.5a1.5 1.5 0 0 1 1.5 1.5v1.5H2.75v-1.5Zm4.5-2.5a1.5 1.5 0 0 1 1.5-1.5h2.5a1.5 1.5 0 0 1 1.5 1.5v1h-5.5v-1Z"></path><path stroke-linecap="round" d="M8.25 10.25v4.5m3.5-4.5v4.5">
	                            </path>
	                        </g>
	                    </svg>
	                </div>
	            </span>
	        </div>
	    </div>
        '''
		else:

			phtml += '''    <div class="post">
        <div class="gutter_l">
            <div class="av">
                <span class="av_icon_container">
                    <button class="av_button button_unstyled">
                        <img class="av_icon" src="'''
			# add avatar url and # todo: add link to profile
			if 'user' in post:
				if post['user'] in avatars:
					user_avatars = avatars[post['user']]
					if mode == 'thread' or mode == 'thread_reply': # we are in /threads/
						phtml += '../'
					phtml += user_avatars['image_48']
				else:
					if mode == 'thread' or mode == 'thread_reply': # we are in /threads/
						phtml += '../'
					user_avatars = avatars['USLACKBOT']
					phtml += user_avatars['image_48']
			else:
				# user isn't found, it has to be a bot - this wasn't finished in time so just make it look like slackbot
				# (the problem is the bots use a different set of keys that I haven't accounted for)
				if mode == 'thread' or mode == 'thread_reply': # we are in /threads/
					phtml += '../'
				user_avatars = avatars['USLACKBOT']
				phtml += user_avatars['image_48']
			phtml += '''">
                    </button>
                </span>
            </div>
        </div>
        '''

	"""		phtml +='''<div class="gutter_r">
            <div class="post_block">
                '''
        # add text
		if 'blocks' in post:

			phtml += blocks_to_html(post['blocks'])


		# add uploads
		if uploads_tup is not None:
			phtml += '<br>' + upload_html
		phtml += '''
            </div>'''

		# todo: add (edited) and tooltip here
		phtml += '''
        </div>
    </div>
    '''
	"""

	if no_avatar or tombstone:
		phtml +='''<div class="gutter_r">'''

	else: # add username and timestamp if avatar
		phtml += '''<div class="gutter_r">
            <span class="sender">
                <a class="sender_link">'''
		# add user name
		phtml += sender_name

		phtml += '''</a>
                
            </span>
             <!-- ws space-->
            <a class="timestamp_link">
                <span class="timestamp">
	                    '''
		# add timestamp
		phtml += timestamp_string

		phtml += '''
                </span>
            </a>
            <br>
            '''
				
	# add broadcast preamble if we are in the main channel
	if 'subtype' in post and mode == 'normal':
		if post['subtype'] == "thread_broadcast":
			phtml += '''<div class="broadcast">
                <span class="broadcast_preamble">replied to a thread: '''

			#thread_origin = threads_dict[thread]
			phtml += '''</span>
                <a class="broadcast_preamble_link" src="javascript:void(0)" onclick="openThread('threads/'''+post['thread_ts']+'''.html')">'''
			# get only the first 30 chars of the original thread
			phtml += post['root']['text'][0:30]
			phtml += '''</a>
            </div>'''
			



	# add post body   (what they wrote)

	phtml += '''
            <div class="post_block">
            '''
	
	if '> has joined the channel' in post['text']:
		phtml += users[post['user']]['name'] + ' has joined the channel'
	else:

		if sender_name == 'Slackbot':

			if post['subtype'] == 'tombstone':
				phtml += '<span class="tombstone_text">This message was deleted</span>'

			elif post['subtype'] != 'slackbot_response':

				print('!! unknown slackbot post encountered !!')
				if 'text' in post:
					phtml += post['text']
				else:
					phtml += '[ERROR: unknown slackbot post type encountered]'
				print(post)
				exit_with_error()
			else:
				text = slackbot_emoji_parser(post['text'])

				print('result of slackbot_emoji_parser: ' + text)
				phtml += text


		# comment support for a long time ago
		# comments are different than a normal post. It just has the 'text' with no formatting
		if is_comment:

			comment_text = post['text']

			formatted_comment_text = ''

			for upload in uploads_tup:
				_, _, file_location, _, thumb_location, _, file_title = upload

				if is_titled_upload:

					if debug: print('is_titled_upload')

					if mode == 'thread' or mode == 'thread_reply':
						file_location = '../' + file_location
						thumb_location = '../' + thumb_location



					formatted_comment_text = users[post['user']]['name']
					formatted_comment_text += ' uploaded a file: <span class="filename">'
					formatted_comment_text += file_title + '</span><br>'
					formatted_comment_text += '<a href="%s"><img src="%s" class="thumbnail" width="270"></a>' %(file_location, thumb_location)

					# formatted_comment_text += clean_slashes(post['text'])

				else:
					if debug: print('is_comment')
					commenter_uid = post['comment']['user']
					commenter = users[commenter_uid]['name']

					formatted_comment_text = '<span class="commenter">' + commenter + '</span> commented on'

					op_uid = post['file']['user']

					commentee = users[op_uid]['name']

					formatted_comment_text = '<span class="commentee">' + commentee + '</span>’s file: '


					if mode == 'thread' or mode == 'thread_reply':
						file_location = '../' + file_location
						thumb_location = '../' + thumb_location

					# insert link to file: comment text

					formatted_comment_text = '<span class="filename">'
					formatted_comment_text += file_title + '</span><br>'
					formatted_comment_text += '<a href="%s"><img src="%s" class="thumbnail" width="270"></a>' %(file_location, thumb_location)

			phtml += formatted_comment_text

			#print(uploads_tup)
			#exit(1)

				
		else: # normal post

			blocks_html = ''

			if 'blocks' in post:


				#print(post)
				blocks_html = blocks_to_html(post['blocks']) # 
				
				#print('\t\t...post added')

			else:
				if debug:
					print('no blocks in post!')

			if blocks_html != '': # no newline if the post was empty
				phtml += blocks_html + '<br>' 

		# add uploads
		if uploads_tup is not None:
			phtml += upload_html

	phtml += '''
            </div>
            '''

	# if 'So I guess you just steal a post' in phtml: # use this to halt on a specific post during debug
	# 	print(post)
	# 	exit(1)

	# add broadcast footer if we are in the main channel
	if 'subtype' in post and mode == 'normal':
		if post['subtype'] == "thread_broadcast":
			phtml += '''<button class="broadcast_footer" onclick="openThread('threads/'''+post['thread_ts']+'''.html')">View newer replies</button>'''

	# add replies count and link (if it is a thread in the main channel)
	if is_thread and mode == 'normal':

		phtml += '''<div class='reply_bar' onclick="openThread('threads/'''+post['ts']+'''.html')">
                '''
					
		# grab repliers avatars (24px)
		reply_users = post['reply_users']

		reply_avatars_max = 8 # only show the first 8 avatars
		reply_avatars_count = 0

		for user in reply_users:
			phtml += '''<span class="reply_bar_avatar">
                    <img class="reply_bar_avatar_image" src="'''
			if mode == 'thread' or mode == 'thread_reply': # go up a dir (we are in /threads)
				phtml += '../'
			phtml += avatars[user]['image_24'] + '''">
                </span>'''

			reply_avatars_count += 1

			if reply_avatars_count == reply_avatars_max:
				print('too many user avatars, hit max. only showing ', reply_avatars_max)
				break

		# next add reply count

		phtml += '''<a class="reply_count">
                    '''
		phtml += str(post['reply_count']) + ''' replies
                </a>'''

		# and add the reply bar description
		phtml += '''<div class="reply_bar_description">
                    <span class="reply_bar_last_reply">
                    '''
            
		# how long after the original post was the latest reply?
		last_reply_string = 'Last reply '

		reply_difference = float(post['latest_reply']) - float(post['thread_ts'])

		#print('reply_difference', reply_difference)

		# todo: there are 2 of these, make a method and consolidate. one is more correct than other.
		if reply_difference/60/60 < 24: # less than 24 hours 
			
			if reply_difference/60 < 60: # less than 60 minutes
				mins_later = math.floor(reply_difference/60)
				have_s = int(mins_later) > 1
				last_reply_string += str(int(mins_later))
				if have_s:
					last_reply_string += ' minutes later'
				else:
					last_reply_string += ' minute later'
			else:
				# above an hour
				hours_later = math.floor(reply_difference/60/60)
				have_s = int(hours_later) > 1
				last_reply_string += str(int(hours_later))
				
				if have_s:
					last_reply_string += ' hours later'
				else:
					last_reply_string += ' hour later'

		else:
			# reply happened days later
			days_later = hours_later = math.floor(reply_difference/60/60/24)
			last_reply_string += str(int(days_later))
			have_s = int(days_later) > 1
			if have_s:
				last_reply_string += ' days later'
			else:
				last_reply_string += ' day later'

		
		phtml += last_reply_string

		phtml += '''
                    </span>
                    <span class="reply_bar_view_thread">
                        View thread
                    </span>
                </div>
                <span class="reply_bar_arrow">&#8250;</span>
            </div>'''


	# todo: need to add attachments too (youtube / spotify links)

	# reactions

	if 'reactions' in post:
		for reaction in post['reactions']:

			emoji_name = reaction['name']

			count = reaction['count']

			reaction_hover_html = ''

			#print('custom emojis: ', emojis)
			#print('looking for emoji: ', emoji_name) # DEL

			# add bigger emoji image
			if emoji_name in emojis: # use custom emoji 
				#print(' its in the custom ones')
				reaction_hover_html = '<img class="big_emoji_in_tooltip" src="'

				reaction_hover_html += emojis[emoji_name] + '"></br>'
			else:
				# fallback to defaults with html

				if emoji_name in emoji_html_map:
					reaction_hover_html += '<span class="big_html_emoji_in_tooltip">' + emoji_html_map[emoji_name] + '</span><br>'
				else:
					# emoji not found.
					reaction_hover_html += '<span class="big_html_emoji_in_tooltip">' + '&#x1F533;' + '</span><br>' # emoji not found is white square

			reacting_users = reaction['users']

			reaction_hover_html += '<span class="users_reaction">' # user names to follow

			for user_i in range(len(reacting_users)):
				cur_user = reacting_users[user_i]
				if user_i == 0:
					reaction_hover_html += users[cur_user]['name'] # add user real name
				elif user_i < len(reacting_users) - 1: # any middle names
					reaction_hover_html += ', ' + users[cur_user]['name']
				else:
					# final name
					reaction_hover_html += ' and ' + users[cur_user]['name']

			reaction_hover_html += '</span><span class="reacted_with">  reacted with :' + emoji_name + ':</span>'


			phtml += '''<div class="reaction_tooltip">'''

			phtml += '''<button class="reaction" type="button">'''


			# emoji link here
			if emoji_name in emojis: # custom emoji
				phtml += '						<img class="small_emoji" src="'
				phtml += emojis[emoji_name] # todo: if we are in a thread, we need to go one deeper. (add '../' to beginning of url)
				phtml += '">'
			elif emoji_name in emoji_html_map:
				phtml += emoji_html_map[emoji_name] # search for emoji in html_map
			else:
				# no emoji (custom or standard) found!
				phtml += '						<img class="small_emoji" src="'
				phtml += emojis['slack'] # default to slack emoji
				phtml += '">'

			phtml += ''' <span class="reaction_count">'''
			phtml += str(count)
			phtml += '''</span></button>
</button>'''
			phtml += '''
						<span class="tooltiptext">'''

			
			# who reacted with this emoji? put it in a hoverable tooltip.

			phtml += reaction_hover_html + '''</span>
</div> '''
			# todo: limit emoji reply tooltip to 45 names ... ? after that it says 'and others'
			# ^^ this isn't really necessary, why don't we just let the million people in there?
	# close out the post
	phtml +='''
        </div>
    </div>
    '''
	# for next time
	last_timestamp_i = timestamp_i

	last_poster = ''
	if 'user' in post:
		last_poster = post['user']
	else:
		last_poster = 'unknown'

	return phtml


def make_html_start(thread=False):
	output = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content=
          "width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../.assets/fonts.css">
    <link rel="stylesheet" href="../.assets/posts.css">
</head>
<body>'''

	if thread == True:
		output = '''<!DOCTYPE html>
	<html lang="en">
	<head>
	    <meta charset="UTF-8">
	    <meta name="viewport" content=
	          "width=device-width, initial-scale=1.0">
	    <link rel="stylesheet" href="../../.assets/fonts.css">
	    <link rel="stylesheet" href="../../.assets/posts.css">
	</head>
	<body>'''
	return output

def make_html_end():
	return '''
</body>
</html>'''


for channel in channels: # we get the keys this way instead of using k,v in dict.items()
	
	# get posts for each day
	files = []
	for (dirpath, dirnames, filenames) in walk(path.join(working_dir, channel)): #getcwd()
		files.extend(filenames)

	#print('files: ', files)

	#print(files)#channel_name = channel['name']

	print('...found %s days of posts in %s' % (len(files), channel))
	channel_path = path.join(working_dir,channel)
	channel_output_path = path.join(output_dir, channel)
	if not path.exists(channel_output_path):
		mkdir(channel_output_path)

	# make threads directory even if not needed
	thread_output_path = path.join(channel_output_path, 'threads')
	if not path.exists(thread_output_path):
		mkdir(thread_output_path)


	# go over each day

	for file in files:


		filepath = path.join(channel_path, file)

		posts = postsimporter.import_posts(
			path_to_import=filepath,
			day_name=file.split('.')[0],
			channel=channel,
			output_dir=output_dir,
			debug=debug)

		print('-----------------')
		if color:
			print(Fore.MAGENTA + Style.BRIGHT + '\tworking on %s : %s' % (channel, file) + Style.RESET_ALL)
		else:
			print('\tworking on %s : %s' % (channel, file))

		# post html buffer
		# add header
		phtml = make_html_start()


		# for up in posts:
		for i in tqdm(range(0, len(posts)), desc ="Generating HTML from posts", leave=False, unit_scale=False):

			#sleep(.1)
			tup = posts[i]

			#for tup in posts: # would be this without tqdm

			post, uploads_tup = tup

			phtml += generate_html_from_post(tup, channel_output_path)



		# add thread viewer panel and script:

		phtml += '''
<div id="threadPanel" class="sidepanel">
	<div class="thread_header_container">
		<div class="thread_header_center">
			<div class="thread_header_content">
				<div class="thread_title">Thread
				
					<div class="thread_subtitle">
						<a class="channel_link" src="''' +' TODO add a channel link'+ '''">
							<span class="thread_subtitle_channel_name">'''
		phtml += '# ' + channel
		phtml += '''</span>
						</a>
					</div>
				</div>
			</div>
			<button class="close_button" onclick="closeThread()">
			<svg data-som="true" viewBox="0 0 20 20" class="" style="--s: 20px;"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.5" d="m5.227 5.227 9.546 9.546m0-9.546-9.546 9.546"></path></svg>
			</button>
		</div>
	</div>
	

	<iframe id="frame" src="threads/1xxxxxxxxx.xxxxxx.html" title="Thread Viewer"></iframe>

</div>

<script>

//var thread_dict = {"123" : "abc"};

function openThread(threadURL) {

	document.getElementById("frame").src = threadURL;
	document.getElementById("threadPanel").style.width = "400px";

	// some text changer
	//var x = document.getElementById("sometext");

	//if (x.innerHTML === "Original Text") {
	//	x.innerHTML = thread_dict["123"];
	//} else {
	//	x.innerHTML = "Original Text";
	//}
}

function closeThread() {
  document.getElementById("threadPanel").style.width = "0";
}
</script>'''

		# × <- fancy x
		phtml += make_html_end()

		if color:
			print(Fore.GREEN + '\t...completed day : ' + file.replace('json', 'html') + Style.RESET_ALL)
		else:
			print('\t...completed day : ' + file.replace('json', 'html'))


		destination = path.join(channel_output_path, file.replace('json', 'html'))
		f = open(destination, "w", encoding="utf8")
		f.write(phtml)
		f.close()



def build_threads_footer(threads_dict, replies_dict):
	global last_poster
	global last_timestamp_i

	# reset to make sure whe have an avatar at the top
	last_timestamp_i = 0
	last_poster = ''

	print('now building threads footer')



	# print('threads_dict')
	# print(threads_dict)
	# print('replies_dict')
	# print(replies_dict)


	#print(threads_dict)


	for thread in threads_dict:
		
		thread_ts = thread
		thread_d = threads_dict[thread]
		thread_tup = thread_d['tup']
		thread_post, thread_uploads_tup = thread_tup
		thread_html_file = thread_d['html']
		thread_anchor = thread_d['anchor']
		thread_channel_path = thread_d['channel_path']

		thread_path = path.join(thread_channel_path, )
		if not path.exists(channel_output_path):
			mkdir(channel_output_path)

		print('building thread:',thread_ts,'...')

		thread_replies = [] # collects all reply posts and the day html in a tuple

		for reply in thread_post['replies']:
			#print(reply)
			reply_ts = reply['ts']

			full_reply = replies_dict[reply_ts]


			

			# print(full_reply)
			reply_tup = full_reply['tup'] # contains the post and upload_tup if needed
			reply_html_file = full_reply['html']

			cleaned_post, uploads_tuple = reply_tup

			to_clean = [
				'client_msg_id',
				'team',
				'user_team',
				'source_team',
				'user_profile'
			]

			# clear a little bit of memory
			for item in to_clean: # this isn't really necessary, and will clean the original also.
				if item in cleaned_post: # but why not save some memory?
					del cleaned_post[item] # remove entry from dict

			#print('cleaned_reply:\n',cleaned_post)
			#print('original_reply:\n',post)

			thread_replies.append((cleaned_post, uploads_tuple)) # todo: this does not account for 'html' when generating the links to the content. may need to pass some other params below when building reply html

			#cleaned_rply


		# print('collected replies:')
		# print(thread_replies)


		thread_html = ''
		op_html = generate_html_from_post(thread_tup, thread_channel_path,
			mode='thread', force_av=True, original_day=thread_html_file)

		thread_html += op_html

		# add the reply line here, and how many replies are there
		thread_html += '''
				<div class="flexpane_separator">
					<div class="flexpane_separator_inner">
						<span class="flexpane_separator_count">''' + str(thread_post['reply_count']) + ''' replies</span>
						<hr class="flexpane_separator_line">
					</div>
				</div>'''


		first_reply = True
		force_av = True

		# TODO: MAKE THIS WORK FOR THE VARIOUS PARTS OF THE POST IMPORTER AND WHATEVER
		#for i in tqdm(range(0, len(thread_replies)), desc ="Building Replies"):
		#		
		#	reply = thread_replies[i]
		#	exit(1)

		# change below to use the above.
		for reply in thread_replies:

			#reply_post, reply_tuple = reply

			reply_html = generate_html_from_post(reply, thread_channel_path,
				force_av=force_av,
				mode='thread_reply',
				original_day=reply_html_file) # reply has diff timestamp
			thread_html += reply_html

			if first_reply:
				first_reply = False
				force_av = False


		print('------------- thread html finished.')

		#print(thread_html)

		thread_html = make_html_start(thread=True) + thread_html + make_html_end()
		

		# save it to 'timestamp'.html

		thread_dir_path = path.join(thread_channel_path, 'threads')
		destination = path.join(thread_dir_path, thread_post['thread_ts'] + '.html')
		f = open(destination, "w", encoding="utf8")
		f.write(thread_html)
		f.close()









build_threads_footer(threads_dict, replies_dict)


print('   Finished: Server Rescued!\n\n   Output: ', output_dir)