## Comp example project ##

The Comp Demo implements two apps, each of which contains a model whose instances can received comments:

 1. App `articles` with the model `Article`
 1. App `quotes` with the model `Quote` contained inside the `extra` directory.
### Features

 1. Comments can be nested, and the maximum thread level is established to 2.
 1. Comment confirmation via mail when the users are not authenticated.
 1. Comments hit the database only after they have been confirmed.
 1. Follow up notifications via mail.
 1. Mute links to allow cancellation of follow-up notifications.
 1. Registered users can like/dislike comments and can suggest comments removal.
 1. Registered users can see the list of users that liked/disliked comments.
 1. The homepage presents the last 5 comments posted either to the `articles.Article` or the `quotes.Quote` model.

#### Threaded comments

The setting `COMMENTS_XTD_MAX_THREAD_LEVEL` is set to 2, meaning that comments may be threaded up to 2 levels below the the first level (internally known as level 0)::
    
    First comment (level 0)
        |-- Comment to "First comment" (level 1)
            |-- Comment to "Comment to First comment" (level 2)

#### `render_xtdcomment_tree`

By using the `render_xtdcomment_tree` templatetag, both, `article_detail.html` and `quote_detail.html`, show the tree of comments posted. `article_detail.html` makes use of the arguments `allow_feedback`, `show_feedback` and `allow_flagging`, while `quote_detail.html` only show the list of comments, with no extra arguments, so users can't flag comments for removal, and neither can submit like/dislike feedback.

#### `render_last_xtdcomments`

The **Last 5 Comments** shown in the block at the rigght uses the templatetag `render_last_xtdcomments` to show the last 5 comments posted to either `articles.Article` or `quotes.Quote` instances. The templatetag receives the list of pairs `app.model` from which we want to gather comments and shows the given N last instances posted. The templatetag renders the template `django_comments_xtd/comment.html` for each comment retrieve.
