# Change Log

## [2.10.6] - 2025-04-07

* Fixes [issue 458](https://github.com/danirus/django-comments-xtd/issues/458) two f-string that were uncompatible with Python < 3.12.
* Rewrites function `get_app_model_options`.
* New tests to cover latest changes.
* Tox now runs tests in both, Python 3.10 and Python 3.13.

## [2.10.5] - 2025-03-22

* Removes external dependencies from `django_comments_xtd/__init__.py`.
* Opens up the range of supported Django versions to "Django>=4,<6".
* Uses `pyproject.toml` to replace `setup.py`.
* Updates `tox.ini`.
* Build JavaScript plugin during CI.
* Replace flake8 with ruff, and adopt pre-commit rules.
* Many stylistic changes after applying ruff.

## [2.10.4] - 2025-03-01

* Updates the version number of the JavaScript plugin to the version of the Python package.

## [2.10.3] - 2025-02-28

* Fixes [issue 451](https://github.com/danirus/django-comments-xtd/issues/451): Exceeding the `COMMENT_MAX_LENGTH` does not reflect in the UI, either when using django templates or when using the JavaScript plugin.

## [2.10.2] - 2025-01-07

* Add reminder about template loading order to the documentation.
* Fix template name `comment_tree.html` in doc strings and the documentation.
* Fix variable template name in `form.html`, in custom example site.
* Remove duplicated code.

## [2.10.1] - 2024-11-28

* Updated French translation.
* Updated battery of tests to check compatibility with Django 5.1.
* GHA: Remove secret from PyPI, as it is now a trusted repository.
* Add support for light/dark color scheme in tutorial.
* Updated example projects: add support for light/dark color schemes.
* Updated dependencies in package.json.
* Updated templates `comments/posted.html`, `comments/preview.html`, and `django_comments_xtd/moderated.html`.
* Docs: Use Bootstrap icon `chat-text-fill.svg` as project's icon.
* Docs: Updated Tutorial. Fixes script example.
* Docs: Use sphinx-nefertiti v0.5 and sphinx-colorschemed-images.

## [2.10.0] - 2024-05-02

 * Add ordering filter to the CommentList API class.
 * Include django-rest-framework v3.15 in tests and example sites.
 * Update tutorial in the documentation.
 * Following templates have changed:
   - `comments/flag.html`
   - `comments/form.html`
   - `django_comments_xtd/comment_tree.html`
   - `django_comments_xtd/dislike.html`
   - `django_comments_xtd/like.html`
   - `django_comments_xtd/reply.html`

## [2.9.13] - 2023-12-22

 * Fixes issue related to missing frontend files within the package distribution.

## [2.9.12] - 2023-12-22

 * Fixes [issue 407](<https://github.com/danirus/django-comments-xtd/issues/377): `ReadCommentSerializer.get_submit_date` does not properly use `DATETIME_FORMAT` setting.
 * Adds the new setting `COMMENTS_XTD_API_DATETIME_FORMAT`.

## [2.9.11] - 2023-12-11

 * Adds support for Django 5.0.

## [2.9.10] - 2023-07-08

 * Updates ReactJS plugin. It has been rewritten to use React Hooks.
 * Add tests to cover over 90% functionality of the JavaScript plugin.
 * Replaces Webpack with Rollup to create the JavaScript bundle.
 * Updates the UI to use Bootstrap 5.3.0.
 * Updates the demo sites to Bootstrap 5.3.0.
 * Extends python tests to Django 4.2 using Python 3.11.
 * Updates the docs.

## [2.9.9] - 2022-10-26

 * Extends compatibility to django-rest-framework v3.14.

## [2.9.8] - 2022-09-18

 * Fixes [issue 377](https://github.com/danirus/django-comments-xtd/issues/377): content_object is missing in followup notification. View `notify_comment_followers` has been updated to include `content_object` in the context of templates it uses: `email_followup_comment.txt` and `email_followup_comment.html`.
 * Update translation files to the latest strings found in templates. Next step is to include appropriate translations. See [PR #379](https://github.com/danirus/django-comments-xtd/pull/379).

## [2.9.7] - 2022-07-08

  * Allows to customize the json object returned by the `get_commentbox_props` template tag. Define the new setting `COMMENTS_XTD_COMMENTBOX_CLASS` as the string path to the class that will return the JSON object. It defaults to the class `django_comments_xtd.api.frontend.CommentBoxDriver`.

## [2.9.6] - 2022-04-07

  * Update version required for django-comments from 2.1 to 2.2.

## [2.9.5] - 2021-12-13

   * Adds compatibility with Django v4.
   * Fixes [issue-358](https://github.com/danirus/django-comments-xtd/issues/358): Missing closing <form> tag in the dislike.html template.

## [2.9.4] - 2021-11-11

   * Fixes [issue-333](https://github.com/danirus/django-comments-xtd/issues/333) produced when using django-comments-xtd with Django 3.2 with MySQL/MariaDB. The issue raises when calling 'update()' on queries with 'sorted_by', as it is the case of the default 'objects' manager of XtdComment.
   * App translation to Simplified Chinesse thanks to @galeo.
   * Fixes issue #334 related to defaults for DRF views. See the [PR-338](https://github.com/danirus/django-comments-xtd/pull/338). Thanks to @PetrDlouhy.
   * Improve command 'populate_xtdcomments' to output using the stdout attribute of the BaseCommand.
   * Fixes [issue-337](https://github.com/danirus/django-comments-xtd/issues/337). Provides updated pyproject.toml file that matches package version.

## [2.9.3] - 2021-09-22

    * Fixes issue in 'models.publish_or_unpublish_nested_comments', when calling the update method on an empty QuerySet. See [issue-318](https://github.com/danirus/django-comments-xtd/issues/318). Thanks to @abiatarfestus, @ironworld and @Khoding.
    * Enhance the queryset in notify_comment_followers using distinct when possible. And fallback to the previous queryset when distinct is not supported, as is the case for sqlite. See [issue-326](https://github.com/danirus/django-comments-xtd/issues/326). Thanks to @enzedonline.

## [2.9.2] - 2021-06-19

    * Fixes issue with nested_count XtdComment's attribute being wrongly computed when comment threads are more than 2 level deep and have more than 1 thread. See [PR-312](https://github.com/danirus/django-comments-xtd/pull/312).
    * Resolves limitation in API views. Avoid using explicit XtdComment model and rather use the `get_model` function to allow using customized comment models with API. See [PR-313](https://github.com/danirus/django-comments-xtd/pull/313). Thanks to @r4fek.
    * Enhance comment form initialization, so that original fields are not override but rather only some of its attributes. See [PR-315](https://github.com/danirus/django-comments-xtd/pull/315). Thanks to @dest81.

## [2.9.1] - 2021-04-14

    * Fixes issue when the 'sent' view does not receive a 'c' query string parameter. See [PR-305](https://github.com/danirus/django-comments-xtd/pull/305). Thanks to @dest81.

## [2.9.0] - 2021-03-20

    * Drops support for Django 2.0 and 2.1.
    * Requires django-contrib-comments >= 2.1, and djangorestframework >= 3.12.
    * Fixes warning when generating the OpenAPI schema. Thanks to @ivanychev. Seee[PR-296](https://github.com/danirus/django-comments-xtd/pull/296).
    * Fixes issue with `render_xtdcomment_tree` templatetag, thanks to @dest81. See [PR-295](https://github.com/danirus/django-comments-xtd/pull/295).
    * Fixes issue #291, about the frontend plugin not being aware of the setting COMMENTS_XTD_DEFAULT_FOLLOWUP. It also fixes the content of the `login_url` props attribute. Its value is now the content of `settings.LOGIN_URL`.
    * Fixes issue #284, about sending a comment twice by clicking the comment send button twice. It happened when not using the JavaScript plugin.

## [2.8.5] - 2021-03-02

    * Fixes issue #292 with the workflow upload-pypi.yml, that caused the package bundle to be built without JavaScript files.

## [2.8.4] - 2021-02-28

    * Adds Italian translation (thanks to @dlrsp-dev).
    * Fixes issue #279, about a syntax mistake in the get_flags function, in the models.py module. Thanks to @manisar2.
    * Fixes issue #271, about an issue with django-comments-xtd data migration 0008. The fix consists of making the migration non-effective. It also requires that the django project developer runs the management command `initialize_nested_count` manually, so that the field `nested_count` of `XtdComment` gets populated with the correct value. The command is idempotent. Thanks to @jxcl.

## [2.8.3] - 2021-02-07

    * Adds new setting COMMENTS_XTD_DEFAULT_FOLLOWUP, which is used to
      initialize the follow-up form field. By default its value is False. Thanks to @drholera. Closes ticket #206.
    * Fixes issue #274, about wrong validation of fields name and email in the
      WriteCommentSerializer. Thanks to @dest81.

## [2.8.2] - 2021-01-24

    * Fixes issue #248, about the API returning comments' submit_date in UTC
      when the setting USE_TZ is enabled and a different TIME_ZONE is given.
      Thanks to @Loneattic.
    * Fixes issue #250, which reports that using the web API to post a comment
      with a reply_to field that would break the max_thread_level should not
      produce an exception but rather a controlled response with an appropriate
      HTTP code. Thanks to @impythonista.
    * Fixes issue #255, about the web API not returning the comment ID when
      creating a new comment. Thanks to @mhoonjeon.
    * Fixes issue #256, about an issue in the JavaScript plugin that displays
      the "reply" link even when the max_thread_level has been reached.
      Thanks to @odescopi.

## [2.8.1] - 2020-10-16

    * Fixes issue #80, that requests to change the response when clicking
      more than once on a comment confirmation link. Up until now clicking
      more than once on a comment confirmation link produced a HTTP 404
      response. Since version 2.8.1 the response is the same as for the first
      click: the user is redirected to the comment's view in the page.
      Thanks to @ppershing.
    * Fixes issue #152, about loading the `staticfiles` templatetag instead of
      `static`. Since Django v3.0 the staticfiles app requires using the
      latter. Thanks to @JonLevy and @mennucc.
    * Fixes issue #221, about the get_version function. Now it returns the full
      version number <major>.<minor>.<patch>. Thanks to @mckinly.
    * Fixes issue #229, about failing to process empty honeypot field when
      posting comments using the REST API. Thanks to @TommasoAmici.

## [2.8.0] - 2020-09-26

    * Fixes issue #106, which is about computing the number of nested comments
      for every comment at every level down the tree. The fix consists of
      adding a new field called 'nested_count' to the XtdComment model. Its
      value represents the number of threaded comments under itself. A new
      management command, 'initialize_nested_count', can be used to update the
      value of the field, the command is idempotent. Two new migrations have
      been added: migration 0007 adds the new field, and migration 0008 calls
      the 'initialize_nested_count' command to populate the nested_count new
      field with correct values.
    * Fixes issue #215 about running the tests with Django 3.1 and Python 3.8.

## [2.7.2] - 2020-09-08

    * Fixes issue #208, about the JavaScript plugin not displaying the like and
      dislike buttons and the reply link when django-comments-xtd is setup to
      allow posting comments only to registered users (who_can_post: "users").
    * Fixes issue #212, about missing i18n JavaScript catalog files for Dutch,
      German and Russian.

## [2.7.1] - 2020-08-12

    * Fixes issue #188, about loading a templatetags module not required for
      the application.
    * Fixes issue #196. When extending django-comments-xtd's comment model, the
      receiver function that reviews whether nested comments have to be publish
      or unpublish is not called.

## [2.7.0] - 2020-08-09

    * Enhancement, closing issue #155 (and #170), on how to post comments via
      the web API. Up until version 2.6.2 posting comments required the fields
      timestamp, security_hash and honeypot. As of 2.7.0 there is support to
      allow Django REST Framework authentication classes: WriteCommentSerializer
      send the signal should_request_be_authorize that enables posting comments.
      Read the documentation about the web API.
    * Enhancement, closing issue #175 on how to customize django-comments-xts
      so that user images displayed in comments come from other sources. A new
      setting COMMENTS_XTD_API_GET_USER_AVATAR has been added. The docs have
      been extended with a page that explains the use case in depth.
    * Fixes issue #171, on wrong permission used to decide whether a user is a
      moderator. The right permission is django_comments.can_moderate.
      (thanks to Ashwani Gupta, @ashwani99).
    * Fixes issue #136 on missing <link> element in the templates/base.html
      file distributed with the tutorial.tar.gz bundle.

## [2.6.2] - 2020-07-05

    * Adds Dutch translation (thanks to Jean-Paul Ladage, @jladage).
    * Adds Russian translation (thanks to Михаил Рыбкин, @MikerStudio).
    * Fixesissue #140, which adds the capacity to allow only registered users
      to post comments.
    * Fixesissue #149, on wrong SQL boolean literal value used when running
      special command populate_xtdcomments to load Postgres database with
      xtdcomments.
    * Fixesissue #154, on using string formatting compatible with Python
      versions prior to 3.6.
    * Fixesissue #156, on wrong props name "poll_interval". JavaScript plugin
      expects uses "polling_interval" while the api/frontend.py module referred
      to itas "poll_interval". (thanks to @ashwani99).
    * Fixesissue #159, about using the same id for all the checkboxes in the
      comment list. When ticking one checkbox in a nested form the checkbox of
      the main form was ticked. Now each checkbox has a different id, suffixed
      with the content of the `reply_to` field.

## [2.6.1] - 2020-05-13

    * Fixes issue #150, about wrong protocol in the URL when fetching avatar
      images from gravatar.

## [2.6.0] - 2020-05-12

    * Fixes issue #145, on inadequate number of SQL queries used by API
      entry point "comments-xtd-api-list", available in the URL
      "/comments/api/<content-type>/<object-pk>/".
      The issue also happened when rendering the comments using tags
      get_xtdcomment_tree and render_xtdcomment_tree. It has been fixed
      in both cases too.
    * Updates the JSON schema of the output retrieved by the API entry
      point "comments-xtd-api-list". Thus the version number change.
      The flags attribute of each retrieved is now a list of flags instead
      of a summary for each the flags: "I like it", "I dislike it",
      "suggest removal".

## [2.5.1] - 2020-04-27

    * Fixes issue #138, on unpublishing a single comment with public nested
      comments. The fix consists of a new pre_save receiver that will
      either publish or unpublish nested comments when a comment changes
      its is_public attribute. (thanks to @hematinik).

## [2.5.0] - 2020-04-22

    * Fixes issue #144 regarding the size of the JavaScript bundle. The
      new JavaScript plugin does not include React and ReactDOM. The two
      libraries have to be loaded with an external script.
    * Update the dependencies of the JavaScript plugin.

## [2.4.3] - 2020-01-26

    * Fixes issue on the ContentType that happens when sending post
      request with empty data. (PR: #137) (thanks to @dvorberg).
    * Adds German translations, (thanks to @dvorberg).

## [2.4.2] - 2019-12-25

    * Adds Django 3.0 compatibility thanks to Sergey Ivanychev (@ivanychev).
    * Adds Norwegian translations thanks to Yngve Høiseth (@yhoiseth).


## [2.4.1] - 2019-09-30

    * Allow changing the "d" parameter when requesting a gravatar,
      thanks to @pylixm (PR: 100).
    * Avoid requiring the SITE_ID, thanks to @gassan (PR: 125).

## [2.4.0] - 2019-02-19

    New minor release thanks to Mandeep Gill with the following changes:

    * Adds support for non-int based object_pk, for instead when using UUIDs or
      HashIds as the primary key on a model (closes #112).
    * Refactors the commentbox props generation into a separate function so can
      be used from the webapi for use with rest_framework/API-only backends that
      don't make use of server-side templates.
    * Adds a pyproject.yaml for use with `poetry` (https://poetry.eustace.io)
      and new pip environments (PEP 518).

## [2.3.1] - 2019-01-08

    * Fixes issue #116.
    * Updates package.json JavaScript dependencies:
       * babel-cli from 6.24.1 to 6.26.0.
       * jquery from 3.2.1 to 3.3.1.

## [2.3.0] - 2018-11-29

    * Upgrades Twitter-Bootstrap from v3 to v4.
    * Fixes issue with tutorial fixtures (bug #114).
    * Upgrade all JavaScript dependencies. Check packages.json for details.
      The major changes are:
       * ReactJS updates from 15.5 to 16.5.
       * Babel updates from 6 to 7.
       * Webpack from 2.4.1 to 4.21.0.
       * Bootstrap from 3.3.7 to 4.1.3.
    * Updates webpack.config.js.
    * Demo sites and tutorial have been adapted to Twitter Bootstrap v4.
    * Fixes issues #94, #108, #111.

## [2.2.1] - 2018-10-06

    * Resolves deprecation warnings and adopt recommendations in unit tests.
    * Fixes demo sites so that they work with Django 1.11, Django 2.0 and
      Django 2.1.

## [2.2.0] - 2018-08-12

    * Adds support for Django 2.1.
    * Drops support for Django < 1.11 as it depends on django-contrib-comments
      which dropped support too.
    * Fixes issue 104 (on lack of Django 2.1 support).

## [2.1.0] - 2018-02-13

    * Fixes issues #76, #86 and #87.
    * Request user name and/or email address in case the user is logged
      in but the user's email attribute is empty and/or the user's
      get_full_name() method returns an empty string.

## [2.0.10] - 2018-01-19

	* Adds Django 2.0 compatibility.
	* Fixes issues #81 and #83.
	* Replaces the use of django.test.client by RequestFactory in unittests.

## [2.0.9] - 2017-11-09

	* Fix issue 77. Template filter xtd_comment_gravatar_url must not
	  hard-code http schema in URL (reported by @pamost).

## [2.0.8] - 2017-09-24

	* App translation to Finnish, thanks to Tero Tikkanen (@terotic).

## [2.0.7] - 2017-09-20

	* Adds missing migration for a field's label (issue 71).
	* Makes the form label for field 'name' translatable (issue 73).

## [2.0.6] - 2017-08-08

	* Code fixes to enable proper support for the Django Sites Framework.
	* Code fixes for the `comp` demo site.
	* Makes demo site dates in initial data files timezone aware.
	* Improves documentation on setting up demo sites.
	* Style changes in CSS wells.

## [2.0.5] - 2017-07-20

	* Surpass version number to fix problem with package upload in PyPI.
	* No changes applied to this version.

## [2.0.4] - 2017-07-19

	* Use `django.core.signing` with temporary comment passed in URL
	  redirection.
	* Fix mistakes in documentation.

## [2.0.3] - 2017-07-10

	* App translation to French thanks to Brice Gelineau.
	* Fixed MANIFEST.in file, so that files with translations are
	  distributed.

## [2.0.0] - 2017-06-04

	* Javascript plugin (based on ReactJS).
	* Web API to:
	  * Create a comment for a given content type and object ID.
	  * List comments for a given content type and object ID.
	  * Send feedback flags (like/dislike) on comments.
	  * Send report flag (removal suggestion) for a comment.
	  * Template filter `has_permission` applicable to a user object and
	    accepting a string specifying the `app_label.permission` being
	    checked. It returns `True` if the user has the given permission,
	    otherwise returns False.
	* Setting `COMMENTS_XTD_API_USER_REPR` defines a lambda function to
	  return the user string representation used by the web API in response
	  objects.
	* Setting `COMMENTS_XTD_APP_MODEL_PERMISSIONS` to explicitly define what
	  commenting features are enabled on per app.model basis.
	* Templates `comments/delete.html` and `comments/deleted.html` matching
	  django-comments-xtd default twitter-bootstrap styling.
	* Dependencies on Python packages: djangorestframework.
	* Supports i18n for English and Spanish.
	* All settings namespaced inside the COMMENTS_XTD setting.
	* Management command to migrate comments from django-contrib-comments to
	  django-comments-xtd.
	* Enable removal link in `django_comments_xtd/comment_tree.html` when the
	  user has the permission `django_comments.can_moderate`.
	* Changed, when the user logged has `django_comments.can_moderate` permission,
	  template `django_comments_xtd/comment_tree.html` will show the number of
	  removal suggestions a comment has received.
	* Changed, when a comment is marked as removed by a moderator
	  (using django-comments' `comments-delete` url) every nested comment below
	  the one removed is unpublished (`is_public` attribute is turned to
	  `False`).
	* Changed view helper functions, `perform_like` and `perform_dislike` now
	  returns a boolean indicating whether a flag was created. If `True` the flag
	  has been created. If `False` the flag has been deleted. These two functions
	  behave as toggle functions.
	* Changed templates `comments/preview.html`, `comments/flag.html` and
	  `comments/flagged.hml`.
	* Removed dependency on django-markup.
	* Removed template filter `render_markup_comment`.
	* Removed setting `MARKUP_FALLBACK_FILTER`.
