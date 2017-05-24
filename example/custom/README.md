## Custom example project ##

The Custom Demo exhibits how to extend django-comments-xtd. This demo used the same **articles** app present in the other two demos, plus:

 * A new django application, called `mycomments`, with a model `MyComment` that extends the `django_comments_xtd.models.MyComment` model with a field `title`.
 
To extend django-comments-xtd follow the next steps:

 1. Set up `COMMENTS_APP` to `django_comments_xtd`
 1. Set up `COMMENTS_XTD_MODEL` to the new model class name, for this demo: `mycomments.models.MyComment`
 1. Set up `COMMENTS_XTD_FORM_CLASS` to the new form class name, for this demo: `mycomments.forms.MyCommentForm`
 1. Change the following templates:
    * `comments/form.html` to include new fields.
    * `comments/preview.html` to preview new fields.
    * `django_comments_xtd/email_confirmation_request.{txt|html}` to add the new fields to the confirmation request, if it was necessary. This demo overrides them to include the `title` field in the mail.
    * `django_comments_xtd/comments_tree.html` to show the new field when displaying the comments. If your project doesn't allow nested comments you can use either this template or `comments/list.html`.
    * `django_comments_xtd/reply.html` to show the new field when displaying the comment the user is replying to.
