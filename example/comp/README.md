## comp demo

This demo implements two apps, each of which contains a model whose instances can received comments:

 1. Django app `articles`, contains the model `Article`
 1. Django app `quotes`, contains the model `Quote`
    
### Features

 1. Comments can be nested, and the maximum thread level is established to 2.
 1. Comment confirmation via mail when the users are not authenticated.
 1. Comments hit the database only after they have been confirmed.
 1. Follow up notifications via mail.
 1. Mute links to allow cancellation of follow-up notifications.
 1. Registered uses can like/dislike comments and can suggest comments removal.

#### Threaded comments

The setting `COMMENTS_XTD_MAX_THREAD_LEVEL` is set to 2, meaning that comments may be threaded up to 2 levels below the the first level (internally known as level 0)::
    
    First comment (level 0)
        |-- Comment to "First comment" (level 1)
            |-- Comment to "Comment to First comment" (level 2)

#### `render_xtdcomment_tree`

Detail templates for articles and quotes show the tree of comments posted by using the templatetag `render_xtdcomment_tree`, which makes use of the template file `django_comments_xtd/comment_tree.html`.

#### `render_last_xtdcomments`

The **Last 5 Comments** shown in the block at the rigght uses the templatetag `render_last_xtdcomments` to show the last 5 comments posted to either `articles.Article` or `quotes.Quote` instances. The templatetag receives the list of pairs `app.model` from which we want to gather comments and shows the given N last instances posted. The templatetag renders the template `django_comments_xtd/comment.html` for each comment retrieve.
