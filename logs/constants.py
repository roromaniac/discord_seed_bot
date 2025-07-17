DISCORD_ID_QUESTION = 'What is your discord ID? This is NOT your username. To find out your Discord ID, right click on your username and select "Copy User ID". You can paste the result here.'
ASYNC_TIME_QUESTION = 'When would you like to play your async? Please use this timestamp tool and copy the first timestamp here.\n\nThe async must be between Jul 24 12:00 EDT and Jul 31 10:00 EDT.'
UNLISTED_STREAM_LINK_QUESTION = "Do you have your own unlisted YouTube channel you want to stream the async to?\n\nPlease don't worry if you don't. We will provide you with a stream key to use if you can't/don't want to use your own.\n\nIf you want to stream to your own unlisted YouTube stream, please ensure you have a stream key granted by YouTube (a process that can take 24 hours if you have never streamed before) BEFORE you submit this form. If you do not provide a stream link that goes live at the time you specified, your async might not get counted."
UNLISTED_STREAM_LINK = 'If you responded "Yes" to having your own stream, please include the stream link to your async.'

# error messages
INVALID_DISCORD_ID = "DISCORD_ID_ERROR: There is no user with this discord id."
INVALID_TIME = "INVALID_TIME_ERROR: The async must be between Jul 24 12:00 EDT and Jul 31 10:00 EDT. Please fill out the form again."
TOO_MANY_ASYNCS = "TOO_MANY_ASYNCS_ERROR: You have already played in the maximum number of allowed asyncs."
STREAM_KEY_NOT_AVAILABLE = "NO_STREAM_KEYS_AVAILABLE: There are no stream keys available at this time. Please DM a Fresh Faces 3 TO to get this resolved ASAP."
OVERLAPPING_ASYNC = 'OVERLAPPING_ASYNC_ERROR: Please allow for at least 3 hours in between async starts.'
INVALID_TIMESTAMP_NOTATION = 'INVALID_TIMESTAMP_ERROR: Please ensure you used the sesh.fyi/timestamp linked in the form and provide the time in <t:(TIMESTAMP):f> format.'
NO_UNLISTED_STREAM_PROVIDED = 'NO_UNLISTED_STREAM_ERROR: You indicated that you wanted to do your own unlisted stream, but did not provide a link. Please fill out the form again.'