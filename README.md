#  django-comments-xtd [![example workflow](https://github.com/danirus/django-comments-xtd/workflows/tests/badge.svg)](https://github.com/danirus/django-comments-xtd/actions/workflows/ci-pipeline.yml)

A Django pluggable application that adds comments to your project.

The current master branch represents is a work-in-progress towards v3.0.0. It has not been released yet as a package in PyPI. The current stable version is based on the branch [v2](https://github.com/danirus/django-comments-xtd/tree/v2) and is [available at PyPI](https://pypi.org/project/django-comments-xtd/).

Example of django-comments-xtd with one thread level and the default theme:

![Example image of using django-comments-xtd](https://github.com/danirus/django-comments-xtd/blob/rel-3.0.0/docs/images/cover.png)

It extends [django-contrib-comments](https://pypi.python.org/pypi/django-contrib-comments) with the following features:

- Thread support, so comments can be nested.
- Customizable maximum thread level, either for all models or on a per app.model basis.
- Optional notifications on follow-up comments via email.
- Mute links to allow cancellation of follow-up notifications.
- Comment confirmation via email when users are not authenticated.
- Comments hit the database only after they have been confirmed.
- Registered users can send reactions to comments, as like/dislike, or other customizable set of reactions.
- Registered users can suggest comment's removal.
- Comment pagination support.
- Template tags to list comments and to add the comment form.
- Emails sent through threads (can be disable to allow other solutions, like a Celery app).
- Fully functional JavaScript plugin (framework free vanilla JavaScript).
- No CSS external dependency.

Example sites and tests work under officially Django `supported versions <https://www.djangoproject.com/download/#supported-versions>`_:

* Django 4.0, 3.2, 3.1
* Python 3.10, 3.9, 3.8

Additional Dependencies:

* django-contrib-comments >=2.1,<2.2
* djangorestframework >=3.12,<3.14

New documentation is going to be provided to cover the new functionalities of django-comments-xtd v3. The documentation for v2 is available [here](http://readthedocs.org/docs/django-comments-xtd/).

## What has changed between v2 and v3

Version 3 of django-comments-xtd is not backward compatible with version 2. Installing v3 will make a site using v2 to fail listing comments. Mainly because there is no `render_xtdcomment_tree` anymore, but rather `render_xtdcomment_list`.

Also because v2's like/dislike flags are gone and replaced by a new `CommentReaction` model.

TODO: There has to be a simple to follow list of steps to migrate from v2 to v3. Write a command line tool if needed. There should be a single page for it in the documentation.
