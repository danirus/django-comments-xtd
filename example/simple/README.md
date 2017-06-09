## Simple example project ##

The Simple Demo features:
  
 1. An Articles App, with a model `Article` whose instances accept comments.
 1. Confirmation by mail is required before the comment hit the database, unless `COMMENTS_XTD_CONFIRM_EMAIL` is set to False. Authenticated users don't have to confirm comments.
 1. Follow up notifications via mail.
 1. Mute links to allow cancellation of follow-up notifications.
 1. It uses the template tag `render_markup_comment` to render comment content. So you can use line breaks, Markdown or reStructuredText to format comments. To use special formatting, start the comment with the line `#!<markup-lang>` being `<markup-lang>` any of the following:
	* markdown
	* restructuredtext
	* linebreaks
 1. No nested comments.
