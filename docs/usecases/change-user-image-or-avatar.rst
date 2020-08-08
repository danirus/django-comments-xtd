.. _ref-change-user-image-or-avatar:

===========================
Change user image or avatar
===========================

.. _Gravatar: http://gravatar.com/
.. _django-avatar: https://github.com/grantmcconnaughey/django-avatar
.. _django-contrib-comments: https://django-contrib-comments.readthedocs.io/

By default django-comments-xtd uses its own template filters to fetch user profile images from Gravatar_ and put them in comments. It is a simple solution that makes the app dependant on an external service. But it is a good solution when the only confirmed record we get from the person who posted the comment is an email address. 

This page describes how to setup django-comments-xtd so that user images displayed in comments come from other sources. For such purpose, in addition to the default filters, we will use django-avatar_. Your Django project can use another application to procure user images, perhaps with a built-in solution or via a social service. Just adapt your case to the methodology exposed here.


.. contents:: Table of Contents
   :depth: 1
   :local:

Purpose
=======

This how-to will combine both solutions, template filters provided with django-comments-xtd and template tags provided with django-avatar, to fetch user images for two different type of comments, those posted by registered users and those posted by mere visitors:

 * Avatar images in comments posted by **non-registered users** will be fetched from Gravatar via django-comments-xtd filters, as the only record we get from those visitors is their email address.
 * On the other hand avatar images in comments posted by **registered users** will be provided by django-avatar templatetags, as django-avatar's templatetags require a user object to fetch the user's image. 

Django-avatar will make those images available from different sources depending on how we customize the app. We can add user images directly using Django's admin interface or we can let the app fetch them via providers, from social networks or writing our own specific provider function.

For the purpose of this how-to we will use the :ref:`example-comp` introduced in the Demo projects page. Before you continue reading please, visit the samples :ref:`example-setup` page and get the :ref:`example-comp` up and running.


Add django-avatar to the Comp project
=====================================

Install django-avatar with ``pip install django-avatar``, and be sure that the ``comp/settings.py`` module contains the following entries:

.. code-block:: python

	MEDIA_ROOT = os.path.join(PROJECT_DIR, "media")
	MEDIA_URL = '/media/'
	INSTALLED_APPS = [
	    ...
	    'avatar',
	    ...
        ]

Then run the migrate command to create django-avatar tables: ``python manage.py migrate``.

Also change the ``comp/urls.py`` module to serve media files in development and get access to users' images stored with django-avatar:

.. code-block:: python

    from django.conf import settings
    from django.conf.urls.static import static

    [...] 
    
    # At the bottom of the module.
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


When using HTML templates to render the comments 
================================================

If your project uses django-comments-xtd HTML templates to render comments, like the Comp project's **quotes app** does, then you only have to adapt your project's HTML templates to use django-avatar.

Let's go then through the following changes:

 * Change the ``comment_tree.html`` template.
 * Create the ``comments/preview.html`` template.
 * Create the ``django_comments_xtd/comment.html`` template (bonus).


Change the ``comment_tree.html`` template
-----------------------------------------

The :ref:`example-comp` uses the **render_xtdcomment_tree** template tag to render the tree of comments in ``quotes/quote_detail.html``. **render_xtdcomment_tree** in turn renders the ``django_comments_xtd/comment_tree.html`` template.

The comp project overrides the ``comment_tree.html`` template. Let's edit it (in ``comp/templates/django_comments_xtd``) to make it start as follows:

.. code-block:: html+django

	{% load l10n %}
	{% load i18n %}
	{% load comments %}
	{% load avatar_tags %}
	{% load comments_xtd %}

	{% for item in comments %}
	<div class="media">
	  <a name="c{{ item.comment.id }}"></a>
	  <img
	    {% if item.comment.user and item.comment.user|has_avatar %}
	      src="{% avatar_url item.comment.user 48 %}"
	    {% else %} 
	      src="{{ item.comment.user_email|xtd_comment_gravatar_url }}"
	    {% endif %}
	    class="mr-3" height="48" width="48"
	  >
	  <div class="media-body">
	    [...]


Create the ``comments/preview.html`` template
---------------------------------------------

We also want to apply the same logic to the ``comments/preview.html`` template. The preview template gets rendered when the user clicks on the preview button in the comment form. 

The ``preview.html`` template is initially served by django-contrib-comments_, but it is overriden by a copy provided from django-comments-xtd templates directory. 

For our purpose we have to modify that version, let's copy it from django-comments-xtd's templates directory into the comp project templates directory:

.. code-block:: bash

    $ cp django_comments_xtd/templates/comments/preview.html example/comp/templates/comments/

And edit the template so that the ``<div class="media">`` starts like this:

.. code-block:: html+django

	{% load avatar_tags %}
	
	[...]

	      <div class="media">
	        <img 
	          {% if request.user|has_avatar %}
	            src="{% avatar_url request.user 48 %}"
	          {% else %}
	            src="{{ form.cleaned_data.user_email|xtd_comment_gravatar_url }}"
	          {% endif %}
	          class="mr-3" width="48" height="48"
	        >
	        <div class="media-body">

	[...]

Create the ``django_comments_xtd/comment.html`` template
--------------------------------------------------------

Additionally to the templates used by the **quotes app**, the :ref:`example-comp` displays a list with the last 5 comments posted to the site, regardless of whether they were sent to the quotes app or the articles app.

In order to get the appropriate avatar images in such a list we need to override the ``django_comments_xtd/comment.html`` template:

.. code-block:: bash

    $ cp django_comments_xtd/templates/django_comments_xtd/comment.html example/comp/templates/django_comments_xtd/

Now edit the template and make the following changes:


.. code-block:: html+django

	{% load avatar_tags %}
	
	[...]

	<div id="c{{ comment.id }}" class="media"><a name="c{{ comment.id }}"></a>
	  <img
	    {% if comment.user|has_avatar %}
	      src="{% avatar_url comment.user 48 %}"
	    {% else %}
	      src="{{ comment.user_email|xtd_comment_gravatar_url }}"
	    {% endif %}
	    height="48" width="48" class="mr-3"
	  >
	  <div class="media-body">

	[...]


Test the changes
----------------

These changes are enough when your project uses only Django templates to render comments. 

Before we can test the solution, let's add an image for the admin user. Do login in the `admin UI <http://localhost:8000>`_ with user/password ``admin/admin`` and click on the avatar application. Add a squared dimensioned image to the admin user.

Now the project is ready to test the two types of comments, a comment sent as a logged-in user and another one sent as a mere visitor:

 1. While you are still logged in in the admin interface, visit the `quotes page <http://localhost:8000/quotes/>`_, click on any of the links and send a comment as the admin user. Sending a comment as a logged in user does not require comment confirmation by email. Therefore you must see already the comment posted in the page and displaying the image you have added to the avatar model using the admin interface. Let's now send a comment as a mere visitor.
 2. `Logout <http://localhost:8000/admin/logout/>`_ from the admin interface and send another comment as a mere visitor. If you have an account in Gravatar_, use an email address of that account for the comment. This way, when you post the comment, you already know what's the image that is going to be displayed from Gravatar. Then send the comment. The email message to confirm the comment is displayed in the console. Scroll up in the console to see the plain-text part of the message and copy the confirmation URL. Then paste it in the browser's location bar to confirm the comment. Once the message is confirmed the comment appears in the quotes page. It should show the image from your Gravatar account.

The message posted as the admin user gets the avatar image from the project's storage using django-avatar's template tag. On the other hand, the image sent as a mere visitor, comes directly from Gravatar using django-comments-xtd's template filter.

When using the web API
======================

If your project uses the web API you have to customize :setting:`COMMENTS_XTD_API_GET_USER_AVATAR` to point to the function that will retrieve the avatar image when the REST API requires it.

The **articles app** of the :ref:`example-comp` uses the web API (actually, the JavaScript plugin does). We have to customize it so that avatar images for registered users are fetched using django-avatar, while avatar images for mere visitors are fetched using the standard Gravatar_ approach.

The default value of :setting:`COMMENTS_XTD_API_GET_USER_AVATAR` points to the function **get_user_avatar** in ``django_comments_xtd/utils.py``. That function only uses Gravatar_ to fetch user images. 

To acomplish it we only need to do the following:

 * Implement the function that fetches images' URLs.
 * Override ``COMMENTS_XTD_API_GET_USER_AVATAR``.
 * Test the changes.


Implement the function that fetches images' URLs
------------------------------------------------

We want to apply the following logic when fetching images' URLs:

 * When a registered user sends a comment, the ``comment.user`` object points to an instance of that user. There we will use **django-avatar** to fetch that uses's image URL.
 * When a mere visitor sends a comment, the ``comment.user`` object is ``None``. But we still have the ``comment.user_email`` which contains the email address of the visitor. Here we will use django-comments-xtd (which in turn defaults to Gravatar).

Create the module ``comp/utils.py`` with the following content:

.. code-block:: python

	from avatar.templatetags.avatar_tags import avatar_url
	from django_comments_xtd.utils import get_user_avatar


	def get_avatar_url(comment):
	    ret = None
	    if comment.user is not None:
	        try:
	            return avatar_url(comment.user)
	        except Exception as exc:
	            pass
	    return get_user_avatar(comment)

If the ``comment`` has a ``user``, we return the result of the ``avatar_url`` function of django-avatar. This function goes through each of the django-avatar providers setup with `AVATAR_PROVIDERS <https://django-avatar.readthedocs.io/en/latest/#AVATAR_PROVIDERS>`_ and returns the appropriate image's URL.

If on the hand the ``comment`` does not have a ``user``, we return what Gravatar has on the ``comment.user_email``. If that email address is not registered in Gravatar, it returns the default image (which you `can customize too <https://en.gravatar.com/site/implement/images/>`_, read in that page from *Default Image* on). 

Override ``COMMENTS_XTD_API_GET_USER_AVATAR``
---------------------------------------------

We have to add a reference to our new function in the settings, to override the content of :setting:`COMMENTS_XTD_API_GET_USER_AVATAR`. Append the following to the ``comp/settings.py` module:

.. code-block:: python

    COMMENTS_XTD_API_GET_USER_AVATAR = "comp.utils.get_avatar_url"


Now the web API will use that function instead of the default one.


Test the changes
----------------

Now the **articles app** is ready. If you already added an avatar image for the admin user, as we did in the previous **Test the changes** section, then send two comments to any of the articles:

 1. Login in as admin/admin in the `admin UI <http://localhost:8000/admin/>`_, then visit any of the `articles page <http://localhost:8000/articles/>`_ and send a comment as the admin user. See also that the image displayed in the preview corresponds to the image added to the admin user.
 2. `Logout <http://localhost:8000/admin/logout/>`_ from the admin interface and send another comment as a mere visitor. If you have a Gravatar account, use the same email address when posting the comment. The Gravatar image associated should be displayed in the comment. 


Conclusion
==========

Images displayed in association with comments can come from customized sources. Adapting your project to use your own sources is a matter of adjusting the templates or writing a new function to feed web API calls.
