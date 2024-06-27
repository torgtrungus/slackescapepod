# Slack EscapePod : a Slack Exporter
- Downloads all posts - including hidden posts older than 90 days - and associated video/image content from Slack.
- Builds an offline, browsable, local copy of the server.
- Supports threads, reactions and custom emojis. Organized by day.
- Rescue your precious shitposts before they are deleted :)


## Instructions

1. **Export Slack Data** - On your Slack's webapp, go to Tools & Settings > Workspace Settings > Import/Export Data (button), and export the zip file of what you want to keep.

2. (optional) **Get app token for custom emojis** by following this [tutorial link](https://api.slack.com/tutorials/tracks/getting-a-token) WITH ANOTHER STEP ADDED:
 - Once you get to the 'Review summary & create your app' screen, edit the configurations. This needs to be added to the list of scopes:
`emoji:read`
Then, continue until you get the token.

3. Run Python script `slackexporter.py`

 - A partial export can be continued by running the script again. It will not re-download content that has already been rescued. You can run it again and it will attempt to complete the 'export'.


## Output

A directory with all content organized first by channel, and then by day - as HTML resembling the Slack web interface (from 2022)




## Notes:

*I had planned to release this eventually but Slack recently announced (6/25/24) they are going to delete content older than 90 days - and maybe people didn't want their content held hostage.*
*This project has incomplete features but should get 95% of everything right - at least as far as my server was set up. For mystery reasons it may not work for you. If so, try to figure it out. I will not provide support - this is basically software you found on the sidewalk and took home. Treat it as such.*


good luck

-TORG
