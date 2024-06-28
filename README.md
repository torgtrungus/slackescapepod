# Slack EscapePod : a Slack Exporter
- Downloads all posts - including hidden posts older than 90 days - and associated video/image content from Slack.
- Builds an offline, browsable, local copy of the server.
- Supports threads, reactions and custom emojis. Organized by day.
- Rescue your precious shitposts before they are deleted on August 26, 2024 :)


![escapepod image with a pixel art craft flying away from a black hole](https://github.com/torgtrungus/slackescapepod/blob/main/logo.png?raw=true 'Escapepod logo')

## Instructions

1. **Export Slack Data** - On your Slack's webapp, go to Tools & Settings > Workspace Settings > Import/Export Data (button), and export the zip file of what you want to keep.

2. (optional) **Get app token to rescue custom emojis** by following this [tutorial link](https://api.slack.com/tutorials/tracks/getting-a-token) *WITH ANOTHER STEP ADDED*:

 - Once you get to the 'Review summary & create your app' screen, edit the configurations:
   This entry needs to be added to the list of Bot Scopes: `- emoji:read`.
 - Then, install the app to the workplace. Follow the prompts to return back to the page that will give you the token.

3. Run Python script `slackexporter.py`

 - A partial export can be continued by running the script again. It will not re-download content that has already been rescued. You can run it again and it will attempt to complete the 'export'.


## Output

A directory with all content organized first by channel, and then by day - as HTML resembling the Slack web interface (from 2022)


## Known Issues

Bot posts may appear blank.

## Notes

*I had planned to release this eventually but Slack recently announced (6/25/24) they are going to delete content older than a year. I figured maybe people didn't want their content held hostage.*
*This project has incomplete features but should get 95% of everything right - at least as far as my server was set up. EscapePod was written on a whim, meant to get to a working state only, so it isn't as pleasant to work with as I'd like. For mystery reasons it may not work for you. If so, try to figure it out. I will not provide support - this is basically software you found on the sidewalk and took home. Treat it as such.*


good luck

-TORG
