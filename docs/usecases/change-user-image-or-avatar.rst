.. _ref-change-user-image-or-avatar:

===========================
Change user image or avatar
===========================

.. _Gravatar: http://gravatar.com/
.. _django-avatar: https://github.com/grantmcconnaughey/django-avatar
.. _django-contrib-comments: https://django-contrib-comments.readthedocs.io/

By default django-comments-xtd uses its own template filters to fetch user profile images from Gravatar_. It is a simple solution that makes the app dependant on an external service. But it is a good solution when the only confirmed record we get from the person who posted the comment is an email address. 

This page describes how to setup django-comments-xtd so that user images displayed in comments come from other sources. For such purpose, in addition to the default filters, we will use django-avatar_. Your Django project can use another application to procure user images, perhaps with a built-in solution or via a social service. Just adapt your case to the methodology exposed here.


.. contents:: Table of Contents
   :depth: 1
   :local:

Purpose
=======

This how-to will combine both, the template filters provided with django-comments-xtd, and the template tags provided with django-avatar. Each application will cover different type of users:

 * Avatar images in comments posted by **non-registered users** will be fetched from Gravatar via django-comments-xtd filters, as the only record we get from those visitors is their email address.
 * On the other hand avatar images in comments posted by **registered users** will be provided by django-avatar templatetags, as django-avatar's templatetags require a user object to fetch the user's image. Django-avatar makes those images available from different sources depending on how we customize the app. We can add them directly using Django's admin interface or we can let the app fetch those images via providers, from social networks or writing our own specific provider function.

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


When using Django to render the comments 
========================================

If your project uses Django in its mature MVC cycle so that django-comments-xtd renders comments using only Django templates, then you only have to adapt your project's HTML templates. Let's go through the changes using the **quotes app** of the :ref:`example-comp`.



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



Testing the changes
-------------------

These changes are enough when your project uses only Django templates to render comments. Now login in `localhost:8000/admin/ <http://localhost:8000>`_ with user/password ``admin/admin``, and visit avatar's admin application to add a squared dimensioned image to the admin user. 

The project is ready to receive two comments, one as a logged-in user and another one as a mere visitor:

 1. While you are still logged in in the admin interface, send one comment as the admin user.
 2. Logout from the admin interface and send another comment as a mere visitor. If you have an account in Gravatar, use an email address of that account for the comment. This way, when you post the comment, you already know what's the image that is going to be displayed from Gravatar. Then send the comment. The email message to confirm the comment is displayed in the console. Scroll up in the console to see the plain-text part of the message and copy the confirmation URL. Then paste it in the browser's location bar to confirm the comment.

The message posted as the admin user gets the avatar image from the project's storage using django-avatar's template tag. On the other hand, the image sent as a mere visitor, comes directly from Gravatar using django-comments-xtd's template filter.

When using Django and the web API
=================================