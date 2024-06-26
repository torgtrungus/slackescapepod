# EscapePod - Slack Exporter
Downloads all posts, video, and image content from Slack, builds a browsable, local copy of the server.
Supports threads, reactions and custom emojis. Organized by day.


## Instructions

1. On your Slack's webapp, go to Tools & Settings > Workspace Settings > Import/Export Data (button), and export the zip file of what you want to keep.

2. Get emoji token by following the [tutorial link](https://api.slack.com/tutorials/tracks/getting-a-token) WITH ANOTHER STEP ADDED:
 - Once you get to the 'Review summary & create your app' screen, edit the configurations. This needs to be added to the list of scopes:
`emoji:read`
Then, continue until you get the token.



*I had planned to release this eventually but as Slack recently (6/25/24) announced they are going to delete content older than 90 days, maybe you don't want your content held hostage.*

## Output

A directory with all content organized by channel, then by day - as HTML.




## Notes:

This project has incomplete features but should get 95% of everything right - at least as far as my server was set up. For mystery reasons it may not work for you. If so, try to figure it out. I will not provide support - this is basically software you found on the sidewalk and took home. Treat it as such.


good luck

-TORG
