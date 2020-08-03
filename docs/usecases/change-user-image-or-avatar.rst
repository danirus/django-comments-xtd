.. _ref-change-user-image-or-avatar:

===========================
Change user image or avatar
===========================

.. _Gravatar: http://gravatar.com/
.. _django-avatar: https://github.com/grantmcconnaughey/django-avatar
.. _django-contrib-comments: https://django-contrib-comments.readthedocs.io/

By default django-comments-xtd uses its own template filters to fetch user profile images from Gravatar_. Such behaviour can be customized. This page describes how to setup django-comments-xtd so that user images displayed in comments can come from a different origin.

For such purpose, in addition to the default filters, we will modify the example projects to make use of django-avatar_. Django-avatar allows registered users' to have their own images stored in the project. This way we won't hit Gravatar every time we display a comment's user image. 

Your Django project may be using another method to procure user images, perhaps it manages them directly or it fetches them using any social service. Just adapt your case to the methodology exposed here.


.. contents:: Table of Contents
   :depth: 1
   :local:

Using only Django templates
===========================

If you don't use django-comments-xtd's web API nor the JavaScript plugin, but just the template based views, you only have to adapt your project's HTML templates. Let's go through the changes using an example project.

A simple example web project using only Django templates to render web pages can be represented by the :ref:`example-simple`. We are going to customize it to display stored user images via django-avatar_. First, visit the samples :ref:`example-setup` page in this documentation to get the :ref:`example-simple` up and running.

By using django-avatar_ we give our project the capacity to store our users' avatar images in our project's storage. Django-avatar's templatetags require an **user** object to fetch users' images. On the other hand django-comments-xtd tags, :ttag:`xtd_comment_gravatar` and :ttag:`xtd_comment_gravatar_url`, use only email addresses. Therefore we can use django-avatar to display registered users' avatars and django-comments-xtd to display visitors' avatars. This way our project will only request external images when the person sending the comment is not a registered user, otherwise it will use the hosted image via django-avatar template tags.

Change the ``settings.py`` module
---------------------------------

Install django-avatar with ``pip install django-avatar``, and be sure that the ``simple/settings.py`` module contains the following entries:

.. code-block:: python

	MEDIA_ROOT = os.path.join(PROJECT_DIR, "media")
	MEDIA_URL = '/media/'
	INSTALLED_APPS = [
	    ...
	    'avatar',
	    ...
        ]

Then run the migrate command to create django-avatar tables: ``python manage.py migrate``.


Change the ``urls.py`` module
-----------------------------

Change the ``simple/urls.py`` module to serve media files in development and get access to users' images stored with django-avatar:

.. code-block:: python

    from django.conf import settings
    from django.conf.urls.static import static

    [...] 
    
    # At the bottom of the module.
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


Change the ``comments/list.html`` template
------------------------------------------

The :ref:`example-simple` uses django-contrib-comments' **render_comment_list** template tag to render the list of comments in ``articles/article_detail.html``. **render_comment_list** in turn renders the ``comments/list.html`` template.

The simple project alredy overrides the ``comments/list.html``. Let's edit it to make it start as follows:

.. code-block:: html+django

	{% load i18n %}
	{% load comments %}
	{% load avatar_tags %}
	{% load comments_xtd %}

	<div id="comments" class="py-3 media-list">
	  {% for comment in comment_list %}
	  <div class="media pb-2">
	    <a name="c{{ comment.id }}"></a>
	    <img 
	      {% if comment.user and comment.user|has_avatar %}
	        src="{% avatar_url comment.user 48 %}"
	      {% else %}
	        src="{{ comment.user_email|xtd_comment_gravatar_url }}"
	      {% endif %} 
	      class="mr-3" width="48" height="48">
	    <div class="media-body">
	    [...]


Create a ``comments/preview.html`` template
-------------------------------------------

We also want to apply the same logic to the ``comments/preview.html`` template. The preview template gets rendered when the user clicks on the preview button in the comment form. 

The ``preview.html`` template is initially served by django-contrib-comments_, but it is overriden by a copy provided from django-comments-xtd templates directory. 

For our purpose we have to modify that version, let's copy it from django-comments-xtd's templates directory into the simple project templates directory:

.. code-block:: bash

    $ cp django_comments_xtd/templates/comments/preview.html example/simple/templates/comments/

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

The simple project is ready. To test it, send a comment as the admin user and another one as a mere visitor (not registered user). When sending the comment as a mere user, the email message to confirm the comment is displayed in the console. Scroll up in the console to see the plain-text part of the message and copy the confirmation URL. Then paste it in the browser.

The message posted as the admin user gets the avatar image from django-avatar, while the image sent as a mere visitor comes directly from Gravatar.

Using the web API or the JavaScript plugin
==========================================