# Change Log

As of version 1.8.0 of django-comments-xtd, all notable changes to this project will be documented in this file.


## [1.8.0] - YYYY-MM-DD

### Added

- Web API to list and create comments. 
- Javascript plugin (ReactJS).
- Setting `COMMENTS_XTD_APP_MODEL_PERMISSIONS` to explicitly define what commenting features are enabled on per app.model basis.
- Templates `comments/delete.html` and `comments/deleted.html` matching django-comments-xtd default twitter-bootstrap styling.

### Changed

- Enable removal link in `django_comments_xtd/comment_tree.html` when the user has the permission `django_comments.can_moderate`.
- When a comment is marked as removed by a moderator (with django-comments' `comments-delete` url) every nested comment below the one removed is unpublished (their is_public attribute is turned False).
- Templates `comments/preview.html`, `comments/flag.html` and `comments/flagged.hml`.
