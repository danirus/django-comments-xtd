## Example Directory ##

Contains three example projects:

 1. Simple
 2. Custom
 3. Comp

### Simple ###

The Simple demo site is a project with an 'articles' application and an 'Article' model whose instances accept comments. It features: 

 * Comments have to be confirmed by mail before they hit the database, unless users are authenticated or `COMMENTS_XTD_CONFIRM_EMAIL` is set to False. 
 * Commenters may request follow up notifications.
 * Mute links to allow cancellation of follow-up notifications.


### Custom ###

The Custom demo exhibits how to extend django-comments-xtd. It uses the same **articles** app present in the other demos, plus:

 * A new application, called `mycomments`, with a model `MyComment` that extends the `django_comments_xtd.models.MyComment` model with a field `title`.
 * Checkout the [custom](https://github.com/danirus/django-comments-xtd/example/custom/) demo directory and [Customizing django-comments-xtd](http://django-comments-xtd.readthedocs.io/en/latest/extending.html) in the documentation.


### Comp ###

The Comp demo implements two apps, each of which contains a model whose instances can received comments:

 1. App `articles` with the model `Article`
 1. App `quotes` with the model `Quote`
    
It features:

 1. Comments can be nested, and the maximum thread level is established to 2.
 1. Comment confirmation via mail when the users are not authenticated.
 1. Comments hit the database only after they have been confirmed.
 1. Follow up notifications via mail.
 1. Mute links to allow cancellation of follow-up notifications.
 1. Registered users can like/dislike comments and can suggest comments removal.
 1. Registered users can see the list of users that liked/disliked comments.
 1. The homepage presents the last 5 comments posted either to the `articles.Article` or the `quotes.Quote` model.
