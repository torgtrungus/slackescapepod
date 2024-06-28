# takes the emoji map from https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json and removes unused content
# this then is used to map reactions in slack with the html renderable unified unicode character

import json

# render in html with
# &#x <code> ;


def unified_to_html(string):
	return '&#x' + string.replace('-', ';&#x') + ';'

f = open('emoji.json', encoding="utf8")
data = json.load(f)





skin_tone_map = {
	'1F3FB' : 'skin-tone-2',
	'1F3FC' : 'skin-tone-3',
	'1F3FD' : 'skin-tone-4',
	'1F3FE' : 'skin-tone-5',
	'1F3FF' : 'skin-tone-6'
}


reduced_dict = {}

for emoji in data:
	for short_name in emoji['short_names']:

		unified = emoji['unified']
		html_emoji = unified_to_html(unified)
		reduced_dict[short_name] = html_emoji

		# note: slack skin variations are not as easy to work with, but not too bad. they are in order (i hope)
		# in reactions, 'skin-tone-2' or 3,4,5,6 are the tones, after the after the short_name, with '::' between them.
		# in the rich text area we get the unified code followed by the skin tone with a '-' between them.
		# to render in html we put it like so: &#xUNICODE;&#xSKINTONEUNICODE;

		if 'skin_variations' in emoji:
			for skin_hex_variation, variation_dict in emoji['skin_variations'].items():
				if '-' in skin_hex_variation: # dealing with 2 people with assigned skin tones
					# these are not supported in reactions. when they are, we have some helper stuff below:
					# hex_tone_a, hex_tone_b = skin_hex_variation.split('-')
					# tone_a_html = unified_to_html(hex_tone_a)
					# tone_b_html = unified_to_html(hex_tone_b)
					# skin_tone_a = skin_tone_map[hex_tone_a]
					# skin_tone_b = skin_tone_map[hex_tone_b]
					pass
				else:
					# non complicated single person skin tone emoji
					skin_tone = skin_tone_map[skin_hex_variation] # look up skin tone string by hex
					html_emoji = unified_to_html(variation_dict['unified'])
					reduced_dict[short_name + '::' + skin_tone] = html_emoji


json_object = json.dumps(reduced_dict)#, indent=4)
 
# Writing to sample.json
with open("emoji_name2unified.json", "w") as outfile:
    outfile.write(json_object)