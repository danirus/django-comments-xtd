## Comp example project ##

The Comp Demo implements two apps:

 1. The `articles` app with the `Article` model.
 1. The `quotes` app with the `Quote` model contained inside the `extra` directory.

### Features

 1. Comments can be nested to a maximum thread level of 2.
 1. Comment confirmation via mail the user is not authenticated.
 1. Comment hit the database only after confirmed.
 1. Follow up notifications via mail.
 1. Mute links to allow cancellation of follow-up notifications.
 1. Registered users can like/dislike comments and suggest removals.
 1. Registered users can see the list of users that liked/disliked comments.
 1. The homepage presents the last 5 comments posted to all apps.

### Threaded comments

The setting `COMMENTS_XTD_MAX_THREAD_LEVEL` is set to 2, meaning that comments can be nested down 2 levels:

    First comment (level 0)
        |-- Comment to "First comment" (level 1)
            |-- Comment to "Comment to First comment" (level 2)
