# Change Log

As of version 1.8.0 of django-comments-xtd, all notable changes to this project will be documented in this file.


## [1.8.0] - YYYY-MM-DD

### Added

- Javascript plugin (based on InfernoJS).
- Web API to:
 * List and create comments.
 * Send feedback flags (like/dislike) on comments.
 * Send report flag (removal suggestion) for a comment.
- Setting `COMMENTS_XTD_API_USER_REPR` defines a lambda function to return the user string representation used by the web API in response objects.
- Setting `COMMENTS_XTD_APP_MODEL_PERMISSIONS` to explicitly define what commenting features are enabled on per app.model basis.
- Templates `comments/delete.html` and `comments/deleted.html` matching django-comments-xtd default twitter-bootstrap styling.

### Changed

- Enable removal link in `django_comments_xtd/comment_tree.html` when the user has the permission `django_comments.can_moderate`.
- When a comment is marked as removed by a moderator (using django-comments' `comments-delete` url) every nested comment below the one removed is unpublished (`is_public` attribute is turned to `False`).
- View helper functions, `perform_like` and `perform_dislike` now returns a boolean indicating whether a flag was created. If `True` the flag has been created. If `False` the flag has been deleted. These two functions behave as toggle functions.
- Templates `comments/preview.html`, `comments/flag.html` and `comments/flagged.hml`.
