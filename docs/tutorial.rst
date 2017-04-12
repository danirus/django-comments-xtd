.. _ref-tutorial:

========
Tutorial
========

This tutorial guides you through the steps to use every feature of django-comments-xtd together with the `Django Comments Framework <https://github.com/django/django-contrib-comments>`_. The Django project used throughout the tutorial is available to `download <https://github.com/danirus/django-comments-xtd/example/tutorial.tar.gz>`_. Following the tutorial will take about an hour, and it is highly recommended to get a comprehensive understanding of django-comments-xtd.

.. contents:: Table of Contents
   :depth: 3
   :local:

.. index::
   single: Installation

Introduction
============

Through the following sections the tutorial will cover the creation of a simple blog with stories to which we will add comments, exercising each and every feature provided by both, django-comments and django-comments-xtd, from comment post verification by mail to comment moderation and nested comments.


.. index::
   single: preparation
   pair: tutorial; preparation
   
Preparation
===========

Before we install any package we will set up a virtualenv and install everything we need in it.

   .. code-block:: bash

       $ mkdir ~/django-comments-xtd-tutorial
       $ cd ~/django-comments-xtd-tutorial
       $ virtualenv venv
       $ source venv/bin/activate
       (venv)$ pip install django-comments-xtd
       (venv)$ wget https://github.com/danirus/django-comments-xtd/demo/tutorial.tar.gz
       (venv)$ tar -xvzf tutorial.tar.gz
       (venv)$ cd tutorial

By installing django-comments-xtd we install all its dependencies, Django and django-contrib-comments among them. So we are ready to work on the project. Take a look at the content of the tutorial directory, it contains:

 * A **blog** app with a **Post** model. It uses two generic class-based views to list the posts, and to show a given post in detail.
 * The **templates** directory, with a **base.html** template, a **home.html** template, and two templates for the blog app: **blog/post_list.html** and **blog/post_detail.html**.
 * The **static** directory with a **css/bootstrap.min.css** file (this file is a static asset available, when the app is installed, under the path **django_comments_xtd/css/bootstrap.min.css**).
 * The **tutorial** directory containing the **settings** and **urls** modules.
 * And a **fixtures** directory with data files to create the *admin* superuser (with *admin* password), the default site and some blog posts.

Let's finish the initial setup, load the fixtures and run the development server:

   .. code-block:: bash

       (venv)$ python manage.py migrate
       (venv)$ python manage.py loaddata fixtures/*.json
       (venv)$ python manage.py runserver

Head to http://localhost:8000 and visit the tutorial site. In the following section we will make changes to enable django-comments-xtd.


.. _configuration:

Configuration
=============

Now that the project is up and running we are ready to add comments. Edit the settings module, ``tutorial/settings.py``, and make the following changes:

   .. code-block:: python

       INSTALLED_APPS = [
           ...
           'django_comments_xtd',
           'django_comments',
           'blog',
       ]
       ...
       COMMENTS_APP = 'django_comments_xtd'

       # Either enable sending mail messages to the console:
       EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

       # Or set up the EMAIL_* settings so that Django can send emails:
       EMAIL_HOST = "smtp.mail.com"
       EMAIL_PORT = "587"
       EMAIL_HOST_USER = "alias@mail.com"
       EMAIL_HOST_PASSWORD = "yourpassword"
       EMAIL_USE_TLS = True
       DEFAULT_FROM_EMAIL = "Helpdesk <helpdesk@yourdomain>"


Edit the urls module of the project, ``democx/democx/urls.py``, to mount the URL patterns of django_comments_xtd to the path ``/comments/``. The urls installed with django_comments_xtd include those required by django_comments too:

   .. code-block:: python

       from django.conf.urls import include, url

       urlpatterns = [
           ...
           url(r'^comments/', include('django_comments_xtd.urls')),
           ...
       ]


Now let Django create the tables for the two new applications:

   .. code-block:: bash

       $ python manage.py migrate


Be sure that the domain field of the ``Site`` instance points to the correct domain, which for the development server is expected to be  ``localhost:8000``. The value is used to create comment verifications, follow-up cancellations, etc. Edit the site instance in the admin interface in case you were using a different value.

After these simple changes the project is ready to use comments, we just need to modify the blog templates.


Comment confirmation
====================

In order to make django-comments-xtd request comment confirmation by mail we need to set the :setting:`COMMENTS_XTD_SALT` setting. This setting helps obfuscating the comment before the user has approved its publication.

This is so because django-comments-xtd does not store comments in the server before they have been confirmed. This way there is little to none possible comment spam flooding in the database. Comments are encoded in URLs and sent for confirmation by mail. Only when the user clicks the confirmation URL the comment lands in the database.

This behaviour is disabled for authenticated users, and can be disabled for anonymous users too by simply setting :setting:`COMMENTS_XTD_CONFIRM_MAIL` to ``False``. 

Now let's append the following entry to the settings module to help obfuscating the comment before it is sent for confirmation:

   .. code-block:: python

       COMMENTS_XTD_SALT = (b"Timendi causa est nescire. "
                            b"Aequam memento rebus in arduis servare mentem.")
                   


Comments tags
=============

In order to be able to post comments to blog stories we need to edit the template file ``blog/post_detail.html`` and load the ``comments`` templatetag module, which is provided by the `Django Comments Framework <https://github.com/django/django-contrib-comments>`_:

   .. code-block:: html+django

       {% load comments %}

We will apply changes in the the blog post detail template:

 #. To show the number of comments posted to the blog story,
 #. To list the comments already posted, and
 #. To show the comment form, so that people can post comments.

By using the :ttag:`get_comment_count` tag we will show the number of comments posted. Change the code around the link element so that it looks like:

   .. code-block:: html+django

       {% get_comment_count for object as comment_count %}
       <div class="text-center" style="padding-top:20px">
         <a href="{% url 'blog:post-list' %}">Back to the post list</a>
         &nbsp;&sdot;&nbsp;
         {{ comment_count }} comments have been posted.
       </div>

Now let's add the code to list the comments posted to the story. We can make use of two template tags, :ttag:`render_comment_list` and :ttag:`get_comment_list`. The former renders a template with the comments while the latter put the comment list in a variable in the context of the template.

When using the first, :ttag:`render_comment_list`, with a ``blog.post`` object, Django will look for the template ``list.html`` in the following directories:

   .. code-block:: shell

       comments/blog/post/list.html
       comments/blog/list.html
       comments/list.html

Both, django-contrib-comments and django-comments-xtd, provide the last of the list. The one in django-comments-xtd includes twitter-bootstrap_ styling. Django will use the first template found, which depends on what application is listed first in :setting:`INSTALLED_APPS`, django-comments-xtd in this case.

Let's modify the ``blog/blog_detail.html`` template to make use of the :ttag:`render_comment_list` tag to add the list of comments. Add the following code at the end of the page, before the ``endblock`` tag:

   .. code-block:: html+django

       {% if comment_count %}
       <div class="comments">
         {% render_comment_list for object %}
       </div>
       {% endif %}
 

Below the list of comments we want to display the comment form, so that users can send their own comments. There are two tags available for the purpose, the :ttag:`render_comment_form` and the :ttag:`get_comment_form`. The former renders a template with the comment form while the latter puts the form in the context of the template giving more control over the fields.

At the moment we will use the first tag, :ttag:`render_comment_form`. Again, add the following code before the ``endblock`` tag:

   .. code-block:: html+django

       {% if object.allow_comments %}
       <div class="comment">
         <h4 class="text-center">Your comment</h4>
         <div class="well">
           {% render_comment_form for object %}
         </div>
       </div>
       {% endif %}
       

Finally, before completing this first set of changes, we could show the number of comments along with post titles in the blog's home page. Let's edit ``blog/post_list.html`` and make the following changes:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load comments %}

       ...
       <p class="date">
         {% get_comment_count for object as comment_count %}
         Published {{ object.publish }}
         {% if comment_count %}
         &sdot;&nbsp;{{ comment_count }} comments
         {% endif %}
       </p>


Now we are ready to send comments. If you are logged in the admin site, your comments won't need to be confirmed by mail. To test the confirmation URL do logout of the admin interface. Bear in mind that :setting:`EMAIL_BACKEND` is set up to send mail messages to the console, so look in the console after you post the comment and find the first long URL in the message. To confirm the comment copy the link and paste it in the location bar of the browser.

The setting :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` is ``0`` by default, which means comments can not be nested. Later in the threads section we will enable nested comments. Now we will set up comment moderation.


.. index::
   single: Moderation

.. _moderation:
   
Moderation
==========

One of the differences between django-comments-xtd and other commenting applications is the fact that by default it requires comment confirmation by email when users are not logged in, a very effective feature to discard unwanted comments. However there might be cases in which we would prefer to follow a different approach. The Django Comments Framework has the `moderation capabilities <http://django-contrib-comments.readthedocs.io/en/latest/moderation.html>`_ upon which we can build our own comment filtering.

Comment moderation is often established to fight spam, but may be used for other purposes, like triggering actions based on comment content, rejecting comments based on how old is the subject being commented and whatnot.

In this section we want to set up comment moderation for our blog application, so that comments sent to a blog post older than a year will be automatically flagged for moderation. Also we want Django to send an email to registered :setting:`MANAGERS` of the project when the comment is flagged.

Let's start adding our email address to the :setting:`MANAGERS` in the ``tutorial/settings.py`` module:

   .. code-block:: python

       MANAGERS = (
           ('Joe Bloggs', 'joe.bloggs@example.com'),
       )


Now we will create a new ``Moderator`` class that inherits from Django Comments Frammework's ``CommentModerator``. This class enables moderation by defining a number of class attributes. Read more about it in `moderation options <https://django-contrib-comments.readthedocs.io/en/latest/moderation.html#moderation-options>`_, in the official documentation of the Django Comments Framework.

We will also register our ``Moderator`` class with the django-comments-xtd's ``moderator`` object. We use django-comments-xtd's object instead of django-contrib-comments' because we still want to have confirmation by email for non-registered users, nested comments, follow-up notifications, etc.

Let's add those changes to the ``blog/model.py`` file:

   .. code-block:: python

       ...
       # Append these imports below the current ones.
       from django_comments.moderation import CommentModerator
       from django_comments_xtd.moderation import moderator

       ...

       # Add this code at the end of the file.
       class PostCommentModerator(CommentModerator):
           email_notification = True
           auto_moderate_field = 'publish'
           moderate_after = 365


       moderator.register(Post, PostCommentModerator)


That makes it, moderation is ready. Visit any of the blog posts with a ``publish`` datetime older than a year and try to send a comment. After confirming the comment you will see the ``django_comments_xtd/moderated.html`` template, and your comment will be put on hold for approval.

If on the other hand you send a comment to a blog post created within the last year your comment will not be put in moderation. Give it a try as a logged in user and as an anonymous user.

When sending a comment to a blog post with a user logged in the comment doesn't have to be confirmed. However, when you send it logged out the comment has to be confirmed by clicking on the confirmation link. Right after clicking on the confirmation link the comment will be put on hold, pending for approval.

In both cases all mail addresses listed in the :setting:`MANAGERS` setting will receive a notification about the reception of a new comment. If you did not received such message, you might need to review your email settings, or the console output. Read about the mail settings above in the :ref:`configuration` section.

A last note on comment moderation: comments pending for moderation have to be reviewed and eventually approved. Don't forget to visit the comments-xtd app in the admin_ interface. Tick the box to select those you want to approve, choose **Approve selected comments** in the **action** dropdown at the top left of the comment list and click on the **Go** button.


Disallow black listed domains
-----------------------------

In the remote case you wanted to disable comment confirmation by mail you might want to set up some sort of control to reject spam.

In this section we will go through the steps to disable comment confirmation while enabling a comment filtering solution based on Joe Wein's blacklist_ of spamming domains. We will also add a moderation function that will put in moderation comments containing badwords_.

Let us first disable comment confirmation, edit the ``tutorial/settings.py`` file and add:

   .. code-block:: python

       COMMENTS_XTD_CONFIRM_EMAIL = False
       

django-comments-xtd comes with a **Moderator** class that inherits from ``CommentModerator`` and implements a method ``allow`` that will do the filtering for us. We just have to change ``blog/models.py`` and replace ``CommentModerator`` with ``SpamModerator``, as follows:

   .. code-block:: python

       # Remove the CommentModerator imports and leave only this:
       from django_comments_xtd.moderation import moderator, SpamModerator

       # Our class Post PostCommentModerator now inherits from SpamModerator
       class PostCommentModerator(SpamModerator):
           ...

       moderator.register(Post, PostCommentModerator)


Now we can add a domain to the ``BlackListed`` model in the admin_ interface. Or we could download a blacklist_ from Joe Wein's website and load the table with actual spamming domains.

Once we have a ``BlackListed`` domain, try to send a new comment and use an email address with such a domain. Be sure to log out before trying, otherwise django-comments-xtd will use the logged in user credentials and ignore the email given in the comment form. Also be sure to post the comment to a story with a publishing date within the last 365 days, otherwise it will enter in moderation regardless of the mail address domain.

Sending a comment with an email address of the blacklisted domain triggers a **Comment post not allowed** response, which would have been a HTTP 400 Bad Request response with ``DEBUG = False`` in production.


Moderate on bad words
---------------------

Let's now create our own Moderator class by subclassing ``SpamModerator``. The goal is to provide a ``moderate`` method that looks in the content of the comment and returns ``False`` whenever it finds a bad word in the message. The effect of returning ``False`` is that comment's ``is_public`` attribute will be put to ``False`` and therefore the comment will be in moderation.

The blog application comes with a bad word list in the file ``blog/badwords.py``

We assume we already have a list of ``BlackListed`` domains and we don't need further spam control. So we will disable comment confirmation by email. Edit the ``settings.py`` file:

   .. code-block:: python

       COMMENTS_XTD_CONFIRM_EMAIL = False


Now edit ``blog/models.py`` and add the code corresponding to our new ``PostCommentModerator``:

   .. code-block:: python

       # Below the other imports:
       from django_comments_xtd.moderation import moderator, SpamModerator
       from blog.badwords import badwords

       ...
       
       class PostCommentModerator(SpamModerator):
           email_notification = True

           def moderate(self, comment, content_object, request):
               # Make a dictionary where the keys are the words of the message and
               # the values are their relative position in the message.
               def clean(word):
                   ret = word
                   if word.startswith('.') or word.startswith(','):
                       ret = word[1:]
                   if word.endswith('.') or word.endswith(','):
                       ret = word[:-1]
                   return ret

               lowcase_comment = comment.comment.lower()
               msg = dict([(clean(w), i)
                           for i, w in enumerate(lowcase_comment.split())])
               for badword in badwords:
                   if isinstance(badword, str):
                       if locase_comment.find(badword) > -1:
                           return True
                   else:
                       lastindex = -1
                       for subword in badword:
                           if subword in msg:
                               if lastindex > -1:
                                   if msg[subword] == (lastindex + 1):
                                       lastindex = msg[subword]
                               else:
                                   lastindex = msg[subword]
                           else:
                               break
                       if msg.get(badword[-1]) and msg[badword[-1]] == lastindex:
                           return True
               return super(PostCommentModerator, self).moderate(comment,
                                                                 content_object,
                                                                 request)

       moderator.register(Post, PostCommentModerator)       


Now we can try to send a comment with any of the bad words listed in badwords_. After sending the comment we will see the content of the ``django_comments_xtd/moderated.html`` template and the comment will be put in moderation.

If you enable comment confirmation by email, the comment will be put on hold after the user clicks on the confirmation link in the email.


.. _admin: http://localhost:8000/admin/
.. _blacklist: http://www.joewein.net/spam/blacklist.htm
.. _badwords: https://gist.github.com/ryanlewis/a37739d710ccdb4b406d


.. index::
   pair: Nesting; Threading
   triple: Maximum; Thread; Level

Threads
=======

Up until this point in the tutorial django-comments-xtd has been configured to disallow nested comments. Every comment is at thread level 0. It is so because by default the setting :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` is set to 0.

When the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` is greater than 0, comments below the maximum thread level may receive replies that will be nested up to the maximum thread level. A comment in a the thread level below the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` can show a **Reply** link that allows users to send nested comments.

In this section we will enable nested comments by modifying :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` and apply some changes to our ``blog_detail.html`` template.

We can make use of two template tags, :ttag:`render_xtdcomment_tree` and :ttag:`get_xtdcomment_tree`. The former renders a template with the comments while the latter put the comments in a nested data structure in the context of the template.

We will also introduce the setting :setting:`COMMENTS_XTD_LIST_ORDER`, that allows altering the default order in which we get the list of comments. By default comments are ordered by thread and their position inside the thread, which turns out to be in ascending datetime of arrival. In this example we would like to list newer comments first.

Let's start by editing ``tutorial/settings.py`` to set up a maximum thread level of 1 and a comment ordering to retrieve newer comments first:

   .. code-block:: python

       COMMENTS_XTD_MAX_THREAD_LEVEL = 1  # default is 0
       COMMENTS_XTD_LIST_ORDER = ('-thread_id', 'order')  # default is ('thread_id', 'order')


Now we have to modify the blog post detail template to load the ``comments_xtd`` templatetag and make use of :ttag:`render_xtdcomment_tree`. We also want to move the comment form from the bottom of the page to a more visible position right below the blog post, followed by the list of comments.

Edit ``blog/post_detail.html`` to make it look like follows:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load comments %}
       {% load comments_xtd %}

       {% block title %}{{ object.title }}{% endblock %}

       {% block content %}
       <h3 class="page-header text-center">{{ object.title }}</h3>
       <p class="small text-center">{{ object.publish|date:"l, j F Y" }}</p>
       <p>
         {{ object.body|linebreaks }}
       </p>
       
       {% get_comment_count for object as comment_count %}
       <div class="text-center" style="padding-top:20px">
         <a href="{% url 'blog:post-list' %}">Back to the post list</a>
         &nbsp;&sdot;&nbsp;
         {{ comment_count }} comments have been posted.  
       </div>

       {% if object.allow_comments %}
       <div class="comment">
         <h4 class="text-center">Your comment</h4>
         <div class="well">
           {% render_comment_form for object %}
         </div>
       </div>
       {% endif %}
       
       {% if comment_count %}
       <hr/>
       <ul class="media-list">
         {% render_xtdcomment_tree for object %}
       </ul>
       {% endif %}
       {% endblock %}


The tag :ttag:`render_xtdcomment_tree` renders the template ``django_comments_xtd/comment_tree.html``.

       
Different max thread levels
---------------------------

There might be cases in which nested comments have a lot of sense and others in which we would prefer a plain comment sequence. We can handle both scenarios under the same Django project with django-comments-xtd.

We just have to use both settings, the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` and :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL`. The former would be set to the default wide site thread level while the latter would be a dictionary of app.model keys and maximum thread level values.

If we wanted to disable nested comments site wide, and enable nested comments up to level one for blog posts, we would need to set it up as follows in our ``settings.py`` module:

   .. code-block:: python

       COMMENTS_XTD_MAX_THREAD_LEVEL = 0  # site wide default
       COMMENTS_XTD_MAX_THREAD_LEVEL_BY_MODEL = {
           # Objects of the app blog, model post, can be nested
           # up to thread level 1.
   	       'blog.post': 1,
       }


Flags
=====

The Django Comments Framework supports `flagging <https://django-contrib-comments.readthedocs.io/en/latest/example.html#flagging>`_ comments, so comments can be flagged for:

 * **Removal suggestion**, when a registered user suggests the removal of a comment.
 * **Moderator deletion**, when a comment moderator marks the comment as deleted.
 * **Moderator approval**, when a comment moderator sets the comment as approved.

django-comments-xtd expands flagging with two more flags:

 * **Liked it**, when a registered user likes the comment.
 * **Disliked it**, when a registered user dislikes the comment.


In this section we will see how to enable a user with the capacity to flag a comment for removal with the **Removal suggestion** flag, how to express likeability, conformity, acceptance or acknowledgement with the **Liked it** flag, and how to express the opposite with the **Disliked it** flag.  

One important requirement to flag a comment is that the user setting the flag must be authenticated. In other words, comments can not be flagged by anonymous users.


Removal suggestion
------------------

Let us enable the comment removal flag. Edit the ``blog/post_detail.html`` template, and at the bottom of the file change the ``render_xtdcomment_tree`` templatetag by adding the argument **allow_flagging**:

   .. code-block:: html+django

       ...
       <ul class="media-list">
         {% render_xtdcomment_tree for object allow_flagging %}
       </ul>


The **allow_flagging** argument makes the templatetag populate a variable ``allow_flagging = True`` in the context in which ``django_comments_xtd/comment_tree.html`` is rendered.

Now let's suggest a removal. First we need to login in the admin_ interface so that we are not an anonymous user. Then we can visit any of the blog posts we sent comments to. When hovering the comments we must see a flag at the right side of the comment's header. After we click on it we land in a page in which we are requested to confirm our removal suggestion. Finally, click on the red **Flag** button to confirm the request.

Once we have flagged a comment we can find the flag entry in the admin_ interface, in the **Comment flags** model, under the Django Comments application. 


Getting notifications
*********************

A user might want to flag a comment on the basis of a violation of our site's terms of use, maybe on hate speech content, racism or the like. To prevent a comment from staying published long after it has been flagged we might want to receive notifications on flagging events.

For such purpose django-comments-xtd provides the class :pclass:`XtdCommentModerator`, which extends django-contrib-comments' :pclass:`CommentModerator`.

In addition to all the `options <https://django-contrib-comments.readthedocs.io/en/latest/moderation.html#moderation-options>`_ of its parent class, :pclass:`XtdCommentModerator` offers the ``removal_suggestion_notification`` attribute, that when set to ``True`` makes Django send a mail to all the :setting:`MANAGERS` on every **Removal suggestion** flag created.

Let's use :pclass:`XtdCommentModerator`, edit ``blog/models.py`` and if you are already using the class ``SpamModerator``, which alreadt inherits from :pclass:`XtdCommentModerator`, just add ``removal_suggestion_notification = True`` to your ``PostCommentModeration`` class. Otherwise add the following code:

   .. code-block:: python

      from django_comments_xtd.moderation import moderator, XtdCommentModerator

      ...
      class PostCommentModerator(XtdCommentModerator):
          removal_suggestion_notification = True

      moderator.register(Post, PostCommentModerator)

Be sure that ``PostCommentModerator`` is the only moderation class registered for the ``Post`` model, and be sure as well that the :setting:`MANAGERS` setting contains a valid email address. The message sent is based on the ``django_comments_xtd/removal_notification_email.txt`` template, already provided within django-comments-xtd. After these changes flagging a comment with a **Removal suggestion** will trigger a notification by mail.


Liked it, Disliked it
---------------------

Django-comments-xtd adds two new flags: the **Liked it** and the **Disliked it** flags.

Unlike the **Removal suggestion** flag, the **Liked it** and **Disliked it** flags are mutually exclusive. So that a user can't like and dislike a comment at the same time, only the last action counts. Users can like/dislike at any time and only the last action will prevail.

In this section we will make changes in the tutorial project to give our users the capacity to like or dislike comments. We will make changes in the ``blog/post_detail.html`` template to introduce a new argument in the **render_xtdcomment_tree** tag:

   .. code-block:: html+django

       <ul class="media-list">
         {% render_xtdcomment_tree for object allow_flagging allow_feedback %}
       </ul>


The **allow_feedback** argument makes the templatetag populate a variable ``allow_feedback = True`` in the context in which ``django_comments_xtd/comment_tree.html`` is rendered.

Having the new like/dislike links in place, if we click on any of them we will end up in either the ``django_comments_xtd/like.html`` or the ``django_comments_xtd/dislike.html`` templates, which are meant to request the user a confirmation for the operation.


.. _show-the-list-of-users:

Show the list of users
**********************

Once the like/dislike flagging is enabled we might want to display the users who actually liked/disliked comments.

Again, by addind an argument to the ``render_xtdcomment_tree`` templatetag we can get rendered the ``includes/django_comments_xtd/user_feedback.html`` with the list of participants.

Change the ``blog/post_detail.html`` to add the argument ``show_feedback``. For this functionality to work we have to add a bit of JavaScript code. As django-comments-xtd templates use twitter-bootstrap_ we will load jQuery and twitter-bootstrap JavaScript libraries from their respective default CDNs too:

   .. code-block:: html+django

       <ul class="media-list">
         {% render_xtdcomment_tree for object allow_flagging allow_feedback show_feedback %}
       </ul>

       {% block extra-js %}
       <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"
           integrity="sha256-k2WSCIexGzOj3Euiig+TlR8gA0EmPjuc79OEeY5L45g="
           crossorigin="anonymous"></script>
       <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
           integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa"
           crossorigin="anonymous"></script>
       <script>
       $(function () {
         $('[data-toggle="popover"]').popover({'html':true})
       })</script>
       {% endblock %}

.. _twitter-bootstrap: http://getbootstrap.com
       

Final notes
===========

We have reached the end of the tutorial. I hope you got enough to start using django-comments-xtd in your own project.

The following page introduces the **Demo projects**. The **simple** demo is a straightforward project to provide comment confirmation by mail, with follow-up notifications and mute links. The **custom** demo is an example about how to extend django-comments-xtd Comment model with new attributes. The **comp** demo shows a project using the complete set of features provided by both django-contrib-comments and django-comments-xtd.

Checkout the **Control Logic** page to understand how django-comments-xtd works along with django-contrib-comments. Read on **Filters and Template Tags** to see in detail the list of template tags and filters offered. The page on **Customizing django-comments-xtd** goes through the steps to extend the app with a quick example and little prose. Read the **Settings** page and the **Templates** page to get to know how you can customize the default behaviour and default look and feel.

If you want to help, please, report any bug or enhancement directly to the github_ page of the project. Your contributions are welcome.

.. _github: https://github.com/danirus/django-comments-xtd
