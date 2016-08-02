.. _ref-tutorial:

========
Tutorial
========

This tutorial guides you through the steps to use every feature of django-comments-xtd together with the `Django Comments Framework <https://github.com/django/django-contrib-comments>`_.

The Django project used throughout the tutorial is available to `download <https://github.com/danirus/django-comments-xtd/demo/bare-project.tar.gz>`_. Use it at your will to apply the changes while reading each section.


.. index::
   single: Installation

Preparation
===========

If you opt for coding the examples, download the bare Django project tarball from this `GitHub page <https://github.com/danirus/django-comments-xtd/demo/bare-project.tar.gz>`_ and decompress it in a directory of your choice.

The most comfortable approach to set it up consist of creating a virtualenv and installing all the dependencies within it. The dependencies are just a bunch of lightweight packages.

   .. code-block:: bash

       $ virtualenv -p python3.5 ~/venv/comments-xtd-tutorial
       $ source ~/venv/comments-xtd-tutorial/bin/activate
       $ cd ~/src
       $ wget https://github.com/danirus/django-comments-xtd/demo/democx.tar.gz
       $ tar -xvzf democx.tar.gz
       $ cd democx
       $ pip install Django
       $ pip install pytz       
       $ sh install.sh
       $ python manage.py runserver


Take a look at the project. The starting point of this tutorial is a simple Django project with a blog application and a few posts. During the following sections we will configure the project to enable comments to the ``Post`` model and try every possible commenting scenario.


.. _configuration:

Configuration
=============

Let us first configure the project to support django-comments and django-comments-xtd. We should start installing the packages and changing the minimum number of settings to enable comments.

   .. code-block:: bash

       $ pip install django-contrib-comments django-comments-xtd \
                     docutils Markdown django-markup

Edit the settings module of the project, ``democx/democx/settings.py``, and make the following changes:

   .. code-block:: python

       INSTALLED_APPS = [
           ...
           'django_comments',
           'django_comments_xtd',
           ...
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
       DEFAULT_FROM_EMAIL = "Helpdesk <helpdesk@yourdomain>"
       

Edit the urls module of the project, ``democx/democx/urls.py``, to mount the URL patterns of django_comments_xtd to the path ``/comments/``. The urls installed with django_comments_xtd include those required by django_comments too:

   .. code-block:: python

       from django.conf.urls import include, url

       urlpatterns = [
           ...
           url(r'^comments/', include('django_comments_xtd.urls')),
           ...
       ]


Let Django create the tables for the two new applications:

   .. code-block:: bash

       $ python manage.py migrate


Be sure that the domain field of the ``Site`` instance points to the correct domain, which is expected to be  ``localhost:8000`` when running the default development server, as it will be used by django_comments_xtd to create comment verification URLs, follow-up cancellation URLs, etc. You can edit the site instance in the admin interface to set it to the right value.


After these simple changes the project is ready to use comments, we just need to modify the templates to include the ``comments`` templatetag module.


Changes in templates
====================

The tutorial project comes ready with a blog application that contains a Post model. Our goal is to provide blog stories with comments, so that people can post comments to the stories and read the comments other people have posted.

The blog application, located in ``democx/blog`` contains a ``blog_detail.html`` template in the ``templates/blog`` directory. We should edit the template and load the ``comments`` templatetag module, which is provided by the `Django Comments Framework <https://github.com/django/django-contrib-comments>`_:

   .. code-block:: html+django

       {% load comments %}


Let's insert now the tags to:

 #. Show the number of comments posted to the blog story,
 #. List the comments already posted, and
 #. Show the comment form, so that people can post comments.

By using the :ttag:`get_comment_count` tag we will show the number of comments posted, right below the text of the blog post. The last part of the template should look like this:

   .. code-block:: html+django

       {% get_comment_count for post as comment_count %}
       <div class="text-center" style="padding-top:20px">
         <a href="{% url 'blog:post_list' %}">Back to the post list</a>
         &nbsp;&sdot;&nbsp;
         {{ comment_count }} comments have been posted.
       </div>

Now let's do the changes to list the comments. We can make use of two template tags, :ttag:`render_comment_list` and :ttag:`get_comment_list`. The former renders a template with the comments while the latter put the comment list in a variable in the context of the template.

When using the first, :ttag:`render_comment_list`, with a ``blog.post`` object, Django will look for the template ``list.html`` in the following directories:

   .. code-block:: shell

       comments/blog/post/list.html
       comments/blog/list.html
       comments/list.html


Let's use :ttag:`render_comment_list` in our ``blog/blog_detail.html`` template to add the list of comments at the end of the page, before the ``endblock`` tag:

   .. code-block:: html+django

       <div class="comments">
         {% render_comment_list for post %}
       </div>
                   

Below the list of comments we want to display the comment form (later we will put the form first), so that users can send their own comments. There are two tags available for such purpose, the :ttag:`render_comment_form` and the :ttag:`get_comment_form`. The former renders a template with the comment form while the latter puts the form in the context of the template giving more control over the fields.

At the moment we will use the first tag, :ttag:`render_comment_form`:

   .. code-block:: html+django

       <div class="comment">
         <h4 class="text-center">Your comment</h4>
         <div class="well">
           {% render_comment_form for post %}
         </div>
       </div>


Finally, before completing this first set of changes, we could show the number of comments along each post title in the blog's home page. We would have to edit the ``blog/home.html`` template and make the following changes:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load comments %}

       ...
       <p class="date">
         {% get_comment_count for post as comment_count %}
         Published {{ post.publish }} by {{ post.author }}
         {% if comment_count %}
         &sdot;&nbsp;{{ comment_count }} comments
         {% endif %}
       </p>


Now we are ready to send comments. If you are logged in the admin site comments do not need to be confirmed by email, and will make it to the application without further intervention. To make django_comments_xtd send a confirmation email do logout of the admin interface before sending the comment.   

By default the setting :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` is ``0``, which means comments can not be nested. In the following sections we will enable threaded comments, we will allow users to flag comments and we will set up comment moderation.


Template Style Customization
============================

In the ``democx`` project we make use of the popular client side web framework, Bootstrap_, which offers the same quick development capacities of Django but in the client side. There are other client side frameworks out there, this example uses Bootstrap_ because it's probably the most popular.

We will adapt our templates to integrate the list of comments and the comment form with the look provided by Bootstrap CSS classes.


Comment list
------------

We should create first a ``comments`` directory inside the templates directory of the ``democx`` project, and then create our own ``list.html`` file inside it with the following code:

   .. code-block:: html+django

       {% load comments %}
       {% load comments_xtd %}

       <ul class="media-list" id="comments">
         {% for comment in comment_list %}
         <li class="media" id="c{{ comment.id }}">
           <div class="media-left">
             <a href="{{ comment.url }}">{{ comment.user_email|xtd_comment_gravatar }}</a>
           </div>
           <div class="media-body">
             <h6 class="media-heading">
               <a class="permalink text-muted" href="{% get_comment_permalink comment %}">¶</a>&nbsp;&sdot;
               {{ comment.submit_date }}&nbsp;-&nbsp;
               {% if comment.url %}<a href="{{ comment.url }}" target="_new">
               {% endif %}{{ comment.name }}{% if comment.url %}</a>{% endif %}
             </h6>
             <p>{{ comment.comment }}</p>
           </div>
         </li>
         {% endfor %}
       </ul>


Form class
----------
       
In order to customize the fields of the comment form we will create a new form class inside the blog application and change the setting :setting:`COMMENTS_XTD_FORM_CLASS` to point to that new form class.

First, create a new file ``forms.py`` inside the ``democx/blog`` directory with the following content:

   .. code-block:: python

       from django.utils.translation import ugettext_lazy as _
       from django_comments_xtd.forms import XtdCommentForm


       class MyCommentForm(XtdCommentForm):
           def __init__(self, *args, **kwargs):
               if 'comment' in kwargs:
                   followup_suffix = ('_%d' % kwargs['comment'].pk)
               else:
                   followup_suffix = ''
               super(MyCommentForm, self).__init__(*args, **kwargs)
               for field_name, field_obj in self.fields.items():
                   if field_name == 'followup':
                       field_obj.widget.attrs['id'] = 'id_followup%s' % followup_suffix
                       continue
                   field_obj.widget.attrs.update({'class': 'form-control'})
                   if field_name == 'comment':
                       field_obj.widget.attrs.pop('cols')
                       field_obj.widget.attrs.pop('rows')
                       field_obj.widget.attrs['placeholder'] = _('Your comment')
                       field_obj.widget.attrs['style'] = "font-size: 1.1em"
                   if field_name == 'url':
                       field_obj.help_text = _('Optional')
               self.fields.move_to_end('comment', last=False)


In ``democx/democs/settings.py`` add the following:

   .. code-block:: python

       COMMENTS_XTD_FORM_CLASS = "blog.forms.MyCommentForm"


Form template
-------------
       
Now we must create a file ``form.html`` within the ``democx/template/comments`` directory containing the code that renders the comment form. It must include each and every visible form field: ``comment``, ``name``, ``email``, ``url`` and ``follow up``:

   .. code-block:: html+django

       {% load i18n %}
       {% load comments %}

       <form method="POST" action="{% comment_form_target %}" class="form-horizontal">
         {% csrf_token %}
         <fieldset>
           <div><input type="hidden" name="next" value="{% url 'comments-xtd-sent' %}"/></div>

           <div class="alert alert-danger hidden" data-comment-element="errors">
           </div>

           {% for field in form %}
             {% if field.is_hidden %}<div>{{ field }}</div>{% endif %}
           {% endfor %}

           <div style="display:none">{{ form.honeypot }}</div>

           <div class="form-group {% if 'comment' in form.errors %}has-error{% endif %}">
             <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
               {{ form.comment }}
             </div>
           </div>

           <div class="form-group {% if 'name' in form.errors %}has-error{% endif %}">
             <label for="id_name" class="control-label col-lg-3 col-md-3">
               {{ form.name.label }}
             </label>
             <div class="col-lg-7 col-md-7">
               {{ form.name }}
             </div>
           </div>

           <div class="form-group {% if 'email' in form.errors %}has-error{% endif %}">
             <label for="id_email" class="control-label col-lg-3 col-md-3">
               {{ form.email.label }}
             </label>
             <div class="col-lg-7 col-md-7">
               {{ form.email }}
               <span class="help-block">{{ form.email.help_text }}</span>
             </div>
           </div>

           <div class="form-group {% if 'url' in form.errors %}has-error{% endif %}">
             <label for="id_url" class="control-label col-lg-3 col-md-3">
               {{ form.url.label }}
             </label>
             <div class="col-lg-7 col-md-7">
               {{ form.url }}
             </div>
           </div>
    
           <div class="form-group">
             <div class="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
               <div class="checkbox">
                 <label for="id_followup{% if cid %}_{{ cid }}{% endif %}">
                   {{ form.followup }}&nbsp;&nbsp;{{ form.followup.label }}
                 </label>
               </div>
             </div>
           </div>  
         </fieldset>
  
         <div class="form-group">
           <div class="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
             <input type="submit" name="post" value="send" class="btn btn-primary" />
             <input type="submit" name="preview" value="preview" class="btn btn-default" />
           </div>
         </div>
       </form>



Preview template
----------------
       
When we click on the preview button Django looks for the ``preview.html`` template in different directories and with different names:

   .. code-block:: shell

       comments/blog_post_preview.html
       comments/blog_preview.html
       comments/blog/post/preview.html
       comments/blog/preview.html
       comments/preview.html


We will provide the last of them by adding the file ``preview.html`` to the ``democx/templates/comments/`` directory with the following code:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}
       {% load comments_xtd %}

       {% block content %}
       <h4>{% trans "Preview your comment:" %}</h4>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           <div class="media">
             {% if not comment %}
             <em>{% trans "Empty comment." %}</em>
             {% else %}
             <div class="media-left">
               <a href="{{ form.cleaned_data.url }}">
                 {{ form.cleaned_data.email|xtd_comment_gravatar }}
               </a>
             </div>
             <div class="media-body">
               <h6 class="media-heading">
                 {% now "N j, Y, P" %}&nbsp;-&nbsp;
                 {% if form.cleaned_data.url %}
                 <a href="{{ form.cleaned_data.url }}" target="_new">{% endif %}
                 {{ form.cleaned_data.name }}
                 {% if form.cleaned_data.url %}</a>{% endif %}
               </h6>
               <p>{{ comment }}</p>
             </div>
             {% endif %}
           </div>
           <div class="visible-lg-block visible-md-block">
             <hr/>
           </div>
         </div>
       </div>
       <div class="well well-lg">
         {% include "comments/form.html" %}
       </div>
       {% endblock %}


Posted template
---------------

Finally, when we hit the send button and the comment gets succesfully processed Django renders the template ``comments/posted.html``. We can modify the look of this template by adding a new ``posted.html`` file to our ``democx/templates/comments`` directory with the following code:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> - 
       <a href="{% url 'blog:post_list' %}">Blog</a>
       {% endblock %}
       
       {% block content %}
       <h3 class="text-center">{% trans "Comment confirmation requested." %}</h3>
       <p>{% blocktrans %}A confirmation message has been sent to your
       email address. Please, click on the link in the message to confirm
       your comment.{% endblocktrans %}</p>
       {% endblock %}

Now we have the form and the core templates integrated with the Bootstrap_ framework. You can visit a blog post and give it a try. Remember that to get the comment confirmation request by email you must sign out of the admin interface.

You might want to adapt the design of the rest of :ref:`ref-templates` provided by django-comments-xtd.

.. _Bootstrap: http://getbootstrap.com


.. index::
   single: Moderation

Moderation
==========

One of the differences between django-comments-xtd and other commenting applications is the fact that by default it requires comment confirmation by email when users are not logged in, a very effective feature to discard unwanted comments. However there might be cases in which we would prefer to apply a different approach to filter incoming comments. The Django Comments Framework has the `moderation capabilities <http://django-contrib-comments.readthedocs.io/en/latest/moderation.html>`_ upon which we can build our own comment filtering.

Comment moderation is often established to fight spam, but may be used for other purposes, like triggering actions based on comment content, rejecting comments based on how old is the subject being commented and whatnot.

In this section we want to set up comment moderation for our blog application, so that comments sent to a blog post older than a year will be automatically flagged for moderation. Also we want Django to send an email to registered :setting:`MANAGERS` of the project when the comment is flagged.

Let's start adding our email address to the :setting:`MANAGERS` in the ``democx/democx/settings.py`` module:

   .. code-block:: python

       MANAGERS = (
           ('Joe Bloggs', 'joe.bloggs@example.com'),
       )


Now we have to create a new ``Moderator`` class that inherits from Django Comments Frammework's ``CommentModerator``. This class enables moderation by defining a number of class attributes. Read more about it in `moderation options <https://django-contrib-comments.readthedocs.io/en/latest/moderation.html#moderation-options>`_, in the official documentation of the Django Comments Framework.

We also need to register our ``Moderator`` class with the django-comments-xtd's ``moderator`` object. We need to use django-comments-xtd's object instead of django-contrib-comments' because we still want to have confirmation by email for non-registered users, nested comments, follow-up notifications, etc.

Let's add those changes to ``democx/blog/model.py`` module:

   .. code-block:: python

       ...
       # New imports to add below the current ones.
       try:
           from django_comments.moderation import CommentModerator
       except ImportError:
           from django.contrib.comments.moderation import CommentModerator

       from django_comments_xtd.moderation import moderator

       ...

       # Add this code at the end of the file.
       class PostCommentModerator(CommentModerator):
           email_notification = True
           auto_moderate_field = 'publish'
           moderate_after = 365

       moderator.register(Post, PostCommentModerator)
       

We may want to customize the look of the ``moderated.html`` template. Let's create the directory ``django_comments_xtd`` under ``democx/templates`` and create inside the file ``moderated.html`` with the following code: 

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}

       {% block title %}{% trans "Comment requires approval." %}{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> - 
       <a href="{% url 'blog:post_list' %}">Blog</a>
       {% endblock %}
       
       {% block content %}
       <h4 class="text-center">{% trans "Comment in moderation" %}</h4>
       <p class="text-center">
       {% blocktrans %}Your comment has to be reviewed before approbal.<br/>
         It has been put automatically in moderation.<br/>
         Thank you for your patience and understanding.{% endblocktrans %}
       </p>
       {% endblock %}


Additionally we need a ``comments/comment_notification_email.txt`` template. This template is used by django-contrib-comments to render the email message that :setting:`MANAGERS` receive when using the moderation option `email_notification <https://django-contrib-comments.readthedocs.io/en/latest/moderation.html#django_comments.moderation.CommentModerator.email_notification>`_, as we do above in our ``PostCommentModerator`` class. Django-comments-xtd comes already with such a template.

Now we are ready to try the moderation in place. Let's visit the web page of a blog post with a ``publish`` datetime older than a year and try to send a comment. After confirming the comment you must be redirected to the ``moderated.html`` template and your comment must be put on hold for approval.

On the other hand if you send a comment to a blog post created within the last year your comment will not be hold for moderation. Exercise it with both, a user logged in (login in the admin_ site with username **admin** and password **admin** will suffice) and logged out (click on **log out** at the top-right corner of the admin_ site).

When sending a comment to a blog post with a user logged in the comment doesn't have to be confirmed. However, when you send it logged out the comment has to be confirmed by clicking on the confirmation link. Right after the user clicks on the link in the confirmation email the comment is put on hold pending for approval.

In both cases, if you have provided an active email address in the :setting:`MANAGERS` setting, you will receive a notification about the reception of a new comment, an email with a subject contaning the site domain within angle brackets. If you did not received such message, you might need to review your email settings. Read above the :ref:`configuration` section and see what are the settings you must enable. Add a hash in front of the :setting:`EMAIL_BACKEND` setting to comment it, this way Django won't use the console to output emails but rather the default email backend along with the rest of email settings provided.

A reminder to finish this section: we need to review those comments put on hold. For such purpose we should visit the comments-xtd app in the admin_ interface. After reviewing the non-public comments, we must tick the box of those we want to approve, select the action **Approve selected comments** and click on the **Go** button.


Disallow black listed domains
-----------------------------

In case you wanted to disable the comment confirmation by email you might be interested in setting up some sort of control to reject spammers. In this section we will go through the steps to disable comment confirmation while enabling a comment filtering solution based on Joe Wein's blacklist_ of spamming domains. We will also add a moderation function that will put on hold comments containing badwords_.

Let us first disable comment confirmation, we need to edit the ``settings.py`` module:

   .. code-block:: python

       COMMENTS_XTD_CONFIRM_EMAIL = False
       

Django-comments-xtd comes with a Moderator class that inherits from ``CommentModerator`` and implements a method ``allow`` that will do the filtering for us. We just have to change our ``democx/blog/models.py`` module and replace ``CommentModerator`` with ``SpamModerator``, as follows:

   .. code-block:: python

       # Remove the CommentModerator imports and leave only this:
       from django_comments_xtd.moderation import moderator, SpamModerator

       # Our class Post PostCommentModerator now inherits from SpamModerator
       class PostCommentModerator(SpamModerator):
           ...

       moderator.register(Post, PostCommentModerator)


Now we can add a domain to the ``BlackListed`` model in the admin_ interface. Or we could download a blacklist_ from Joe Wein's website and load the table with actual spamming domains.

Once we have a ``BlackListed`` domain we can try to send a new comment and use an email address with such a domain. Be sure to log out before trying, otherwise django-comments-xtd will use the logged in user credentials and ignore the email given in the comment form.

Sending a comment with an email address of the blacklisted domain triggers a **Comment post not allowed** response, which would have been a HTTP 400 Bad Request response with ``DEBUG = False`` in production.


Moderate on bad words
---------------------

Let us now create our own Moderator class by subclassing ``SpamModerator``. The goal is to provide a ``moderate`` method that looks in the content of the comment and returns ``False`` whenever it finds a bad word in the message. The effect of returning ``False`` is that the comment's ``is_public`` attribute will be put to ``False`` and therefore the comment will be on hold waiting for approval.

The blog application comes already with what we are going to consider a bad word (for the purpose of this tutorial, we will use this badwords_ list), which are listed in the ``democx/blog/badwords.py`` module.

We will assume that we already have a list of ``BlackListed`` domains in our database, as explained in the previous section, and we don't want further spam control, so we want to disable comment confirmation by email. Let's edit the ``settings.py`` module:

   .. code-block:: python

       COMMENTS_XTD_CONFIRM_EMAIL = False


Then let's edit the ``democx/blog/models.py`` module and add the following code corresponding to our new ``PostCommentModerator``:

   .. code-block:: python

       # Below the other imports:
       from django_comments_xtd.moderation import moderator, SpamModerator
       from .badwords import badwords

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
               
               msg = dict([(clean(w), i)
                           for i, w in enumerate(comment.comment.lower().split())])
               for badword in badwords:
                   if isinstance(badword, str):
                       if badword in msg:
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


Now we can send a comment to a blog post and put any of the words listed in the badwords_ list in the message. After clicking on the send button we must see the ``moderated.html`` template and the comment must be put on hold for approval.

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

When the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` is greater than 0, comments below the maximum thread level may receive replies that will be nested up to the maximum thread level. A comment in a the thread level below the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` will show a **Reply** link that allows users to send nested comments.

In this section we will enable nested comments by modifying :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` and apply some changes to our ``blog_detail.html`` template. We will use the tag :ttag:`get_xtdcomment_tree` that retrieves the comments in a nested data structure, and we will create a new template to render the nested comments.

We will also introduce the setting :setting:`COMMENTS_XTD_LIST_ORDER`, that allows altering the default order in which we get the list of comments. By default comments are ordered by thread and their position inside the thread, which turns out to be in ascending datetime of arrival. In this example we would like to list newer comments first.

Let's start by editing the ``democx/democx/settings.py`` module to set up a maximum thread level of 1 and a comment ordering to retrieve newer comments first:

   .. code-block:: python

       COMMENTS_XTD_MAX_THREAD_LEVEL = 1  # default is 0
       COMMENTS_XTD_LIST_ORDER = ('-thread_id', 'order')  # default is ('thread_id', 'order')


Now we have to modify the blog post detail template to load the ``comments_xtd`` templatetag module and make use of the :ttag:`get_xtdcomment_tree` tag. We also want to move the comment form from the bottom of the page to a more visible position right below the blog post, followed by the list of comments.

Let's edit ``democx/blog/templates/blog/blog_detail.html`` to make it look like follows:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load comments %}
       {% load comments_xtd %}

       {% block title %}{{ post.title }}{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> -
       <a href="{% url 'blog:post_list' %}">Blog</a>
       {% endblock %}

       {% block content %}
       <h3 class="page-header text-center">My blog</h3>
       <h4>{{ post.title }}</h4>
       <p class="date">
         Published {{ post.publish }} by {{ post.author }}
       </p>
       {{ post.body|linebreaks }}

       {% get_comment_count for post as comment_count %}
       <div class="post-footer text-center">
         <a href="{% url 'blog:post_list' %}">Back to the post list</a>
         &nbsp;&sdot;&nbsp;
         {{ comment_count }} comments have been posted.  
       </div>

       <div class="well">
         {% render_comment_form for post %}
       </div>

       {% if comment_count %}
       <hr/>
       <ul class="media-list">
         {% get_xtdcomment_tree for post as comments_tree %}
         {% include "blog/comments_tree.html" with comments=comments_tree %}
       </ul>
       {% endif %}
       {% endblock %}

At the end of the file we use another template to render the list of comments. This template will render all the comments in the same thread level and will call itself to render those in nested levels. Let's create the template ``blog/comments_tree.html`` and add the following code to it:

   .. code-block:: html+django

       {% load i18n %}
       {% load comments %}
       {% load comments_xtd %}

       {% for item in comments %}
       {% if item.comment.level == 0 %}
       <li class="media">{% else %}<div class="media">{% endif %}
         <a name="c{{ item.comment.id }}"></a>
         <div class="media-left">{{ item.comment.user_email|xtd_comment_gravatar }}</div>
         <div class="media-body">
           <div class="comment">
             <h6 class="media-heading">
               {{ item.comment.submit_date }}&nbsp;-&nbsp;{% if item.comment.url and not item.comment.is_removed %}<a href="{{ item.comment.url }}" target="_new">{% endif %}{{ item.comment.name }}{% if item.comment.url %}</a>{% endif %}&nbsp;&nbsp;<a class="permalink" title="comment permalink" href="{% get_comment_permalink item.comment %}">¶</a>
             </h6>
             {% if item.comment.is_removed %}
             <p>{% trans "This comment has been removed." %}</p>
             {% else %}
             <p>
               {{ item.comment.comment|render_markup_comment }}
               <br/>
               {% if item.comment.allow_thread and not item.comment.is_removed %}
               <a class="small mutedlink" href="{{ item.comment.get_reply_url }}">
                 {% trans "Reply" %}
               </a>
               {% endif %}
             </p>
             {% endif %}
           </div>
           {% if not item.comment.is_removed and item.children %}
           <div class="media">
             {% include "blog/comments_tree.html" with comments=item.children %}
           </div>
           {% endif %}
         </div>
       {% if item.comment.level == 0 %}
       </li>{% else %}</div>{% endif %}
       {% endfor %}

This template uses the tag :ttag:`xtd_comment_gravatar` included within the ``comments_xtd.py`` templatetag module, that loads the gravatar image associated with an email address. It also uses :ttag:`render_markup_comment`, that will render the comment using either markdown, restructuredtext, or linebreaks. 

Another important remark on this template is that it calls itself recursively to render nested comments for each comment. The tag :ttag:`get_xtdcomment_tree` retrieves a list of dictionaries. Each dictionary contains two attributes: ``comment`` and ``children``. The attribute ``comment`` is the ``XtdComment`` object and the attribute ``children`` is another list of dictionaries with the nested comments.

We don't necessarily have to use :ttag:`get_xtdcomment_tree` to render nested comments. It is possible to render them by iterating over the list of comments and accessing the level attribute. Take a look at the ``simple_threaded`` demo project, the ``list.html`` template iterates over the list of comments adding an increasing left padding depending on the thread level the comment belongs to.

Finally we might want to adapt the ``django_comments_xtd/reply.html`` template, that will be rendered when the user clicks on the reply link:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}
       {% load comments %}
       {% load comments_xtd %}

       {% block title %}{% trans "Comment reply" %}{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> -
       <a href="{% url 'blog:post_list' %}">Blog</a> -
       <a href="{{ comment.content_object.get_absolute_url }}">{{ comment.content_object }}</a>
       {% endblock %}

       {% block content %}
       <h4 class="page-header text-center">{% trans "Reply to comment" %}</h4>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           <div class="media">
             <div class="media-left">
               {% if comment.user_url %}
               <a href="{{ comment.user_url }}">
                 {{ comment.user_email|xtd_comment_gravatar }}
               </a>
               {% else %}
               {{ comment.user_email|xtd_comment_gravatar }}
               {% endif %}
             </div>
             <div class="media-body">
               <h6 class="media-heading">
                 {{ comment.submit_date|date:"N j, Y, P" }}&nbsp;-&nbsp;
                 {% if comment.user_url %}
                 <a href="{{ comment.user_url }}" target="_new">{% endif %}
                 {{ comment.user_name }}{% if comment.user_url %}</a>{% endif %}
               </h6>
               <p>{{ comment.comment }}</p>
             </div>
           </div>
           <div class="visible-lg-block visible-md-block">
             <hr/>
           </div>
         </div>
       </div>
       <div class="well well-lg">
         {% include "comments/form.html" %}
       </div>
       {% endblock %}


Different max thread levels
---------------------------

There might be cases in which nested comments have a lot of sense and others in which we would prefer a plain comment sequence. We can handle both scenarios under the same Django project with django-comments-xtd.

We just have to use both settings, the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` and :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL`. The former would be set to the default wide site thread level while the latter would be a dictionary of app.model literals as keys and the corresponding maximum thread level as values.

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

The Django Comments Framework comes with support for `flagging <https://django-contrib-comments.readthedocs.io/en/latest/example.html#flagging>`_ comments, so that a comment can receive the following flags:

 * **Removal suggestion**, when a registered user suggests the removal of a comment.
 * **Moderator deletion**, when a comment moderator marks the comment as deleted.
 * **Moderator approval**, when a comment moderator sets the comment as approved.

Django-comments-xtd extends the functionality provided by django-contrib-comments with two more flags:

 * **Liked it**, when a registered user likes the comment.
 * **Disliked it**, when a registered user dislikes the comment.


In this section we will see how to enable a user with the capacity to flag a comment for removal with the **Removal suggestion** flag, how to express likeability, conformity, acceptance or acknowledgement with the **Liked it** flag, and how to express the opposite with the **Disliked it** flag.  

One important requirement to flag a comment is that the user setting the flag must be authenticated. In other words, comments can not be flagged by anonymous users.


Removal suggestion
------------------

Let us start by enabling the link that allows a user to suggest a comment removal. This functionality is already provided by django-contrib-comments. We will simply put it in the template.

To place the flag link we need to edit the ``blog/comments_tree.html`` template. We will show the flag link at the right side of the comment's header:

   .. code-block:: html+django

       ...
       {% for item in comments %}
         ...
               <h6 class="media-heading">
                 {{ item.comment.submit_date }}&nbsp;-&nbsp;
                 {% if item.comment.url and not item.comment.is_removed %}
                 <a href="{{ item.comment.url }}" target="_new">{% endif %}
                   {{ item.comment.name }}{% if item.comment.url %}
                 </a>{% endif %}&nbsp;&nbsp;
                 <a class="permalink" href="{% get_comment_permalink item.comment %}">¶</a>

                 <!-- Add this to enable flagging a comment -->
                 {% if request.user.is_authenticated %}
                 <div class="pull-right">
                   <a class="mutedlink" href="{% url 'comments-flag' item.comment.pk %}">
                     <span class="glyphicon glyphicon-flag" title="flag comment"></span>
                   </a>
                 </div>       
                 {% endif %}                 
               </h6>
         ...

Additionally we might want to adapt the style of two related templates: ``comments/flag.html`` and ``comments/flagged.html``. The first presents a form to the user to confirm the removal suggestion, while the second renders a confirmation message once the user has flagged the comment.

Let's create the template ``flag.html`` in the directory ``democx/templates/comments`` with this content:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}
       {% load comments_xtd %}

       {% block title %}{% trans "Flag this comment" %}{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> -
       <a href="{% url 'blog:post_list' %}">Blog</a> -
       <a href="{{ comment.content_object.get_absolute_url }}">{{ comment.content_object }}</a>
       {% endblock %}

       {% block content %}
       <h4 class="page-header text-center">{% trans "Really flag this comment?" %}</h4>
       <p class="text-center">{% trans "Click on the flag button if you want to suggest the removal of the following comment:" %}</p>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           <div class="media">
             <div class="media-left">
               {% if comment.user_url %}
               <a href="{{ comment.user_url }}">
                 {{ comment.user_email|xtd_comment_gravatar }}
               </a>
               {% else %}
               {{ comment.user_email|xtd_comment_gravatar }}
               {% endif %}
             </div>
             <div class="media-body">
               <h6 class="media-heading">
                 {{ comment.submit_date|date:"N j, Y, P" }}&nbsp;-&nbsp;
                 {% if comment.user_url %}
                 <a href="{{ comment.user_url }}" target="_new">{% endif %}
                   {{ comment.user_name }}
                   {% if comment.user_url %}
                 </a>{% endif %}
               </h6>
               <p>{{ comment.comment }}</p>
             </div>
           </div>
           <div class="visible-lg-block visible-md-block">
             <hr/>
           </div>
         </div>
       </div>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           <div class="well well-lg">
             <form action="." method="post" class="form-horizontal">{% csrf_token %}
               <div class="form-group">
                 <div class="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
                   <input type="submit" name="submit" class="btn btn-danger" value="{% trans "Flag" %}"/>
                   <a class="btn btn-default" href="{{ comment.get_absolute_url }}">cancel</a>
                 </div>
               </div>
             </form>
           </div>
         </div>
       </div>
       {% endblock %}

And the template ``flagged.html`` in the same directory ``democx/templates/comments`` with the code:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}
       {% load comments_xtd %}

       {% block title %}{% trans "Thanks for flagging" %}.{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> -
       <a href="{% url 'blog:post_list' %}">Blog</a> -
       <a href="{{ comment.content_object.get_absolute_url }}">{{ comment.content_object }}</a>
       {% endblock %}

       {% block content %}
       <h4 class="page-header text-center">Thanks for flagging</h4>
       <p class="text-center">{% trans "Thank you for taking the time to improve the quality of discussion in our site." %}<p>
       {% endblock %}


Now we can try it, let's suggest a removal. First we need to login in the admin_ interface so that we are not an anonymous user. Then we can visit any of the blog posts to which we have sent comments. When hovering the comments we must see a flag at the right side of the comment's header. If we click on it we will land in the page where we are requested to confirm our suggestion to remove the comment. If we click on the red **Flag** button we will create the **Removal suggestion** flag for the comment.

Once we have flagged a comment we can find the flag entry in the admin_ interface, under the **Comment flags** model, under the Django Comments application. 


Getting notifications
*********************

A user might want to flag a comment on the basis of a violation of our site's terms of use, maybe on hate speech content, racism or the like. To prevent a comment from staying published long after it has been flagged we might want to receive notifications on flagging events.

For such purpose django-comments-xtd provides the class :pclass:`XtdCommentModerator`, which extends django-contrib-comments' :pclass:`CommentModerator`.

In addition to all the `options <https://django-contrib-comments.readthedocs.io/en/latest/moderation.html#moderation-options>`_ offered by the parent class :pclass:`XtdCommentModerator` exposes the attribute ``removal_suggestion_notification``. When this attribute is set to ``True`` Django will send an email to the :setting:`MANAGERS` on every **Removal suggestion** flag created.

Let's use :pclass:`XtdCommentModerator` in our demo. If you are using the class ``SpamModerator`` already in the ``democx/blog/models.py`` module, then simply add ``removal_suggestion_notification = True`` to your Moderation class, as ``SpamModerator`` already inherits from ``XtdCommentModerator``. Otherwise add the following code:

   .. code-block:: python

      from django_comments_xtd.moderation import moderator, XtdCommentModerator

      ...
      class PostCommentModerator(XtdCommentModerator):
          removal_suggestion_notification = True

      moderator.register(Post, PostCommentModerator)

Be sure that ``PostCommentModerator`` is the only moderation class registered for the ``Post`` model, and be sure as well that the :setting:`MANAGERS` setting contains a valid email address. The email is based on the template ``django_comments_xtd/removal_notification_email.txt`` already provided within the django-comments-xtd app. After these changes flagging a comment with a **Removal suggestion** must trigger an email.


Liked it, Disliked it
---------------------

Django-comments-xtd adds two new flags: the **Liked it** and the **Disliked it** flags.

Unlike the **Removal suggestion** flag, the **Liked it** and **Disliked it** flags are mutually exclusive. So that a user can't like and dislike a comment at the same time, only the last action counts. Users can click on the links at any time and only the last action will prevail.

In this section we will make changes in the ``democx`` project to give our users the capacity to like or dislike comments. We can start by adding the links to the ``comments_tree.html`` template. The links could go immediately after rendering the comment content, at the left side of the Reply link:

   .. code-block:: html+django

       ...
               <p>
                 {{ item.comment.comment|render_markup_comment }}
                 <br/>
                 <!-- Add here the links to let users express whether they like the comment. -->
                 <a href="{% url 'comments-xtd-like' item.comment.pk %}" class="mutedlink">
                   <span class="small">{{ item.likedit|length }}</span>&nbsp;
                   <span class="small glyphicon glyphicon-thumbs-up"></span>
                 </a>
                 <span class="text-muted">&sdot;</span>
                 <a href="{% url 'comments-xtd-dislike' item.comment.pk %}" class="mutedlink">
                   <span class="small">{{ item.dislikedit|length }}</span>&nbsp;
                   <span class="small glyphicon glyphicon-thumbs-down"></span>
                 </a>
                 <span class="text-muted">&sdot;</span>
                 <!-- And the reply link -->
                 {% if item.comment.allow_thread and not item.comment.is_removed %}
                 <a class="small mutedlink" href="{{ item.comment.get_reply_url }}">
                   {% trans "Reply" %}
                 </a>
                 {% endif %}
               </p>
       ...


Having the links in place, if we click on any of them we will end up in either the ``like.html`` or the ``dislike.html`` templates. These two templates are new, and meant to request the user to confirm the operation.

We can create new versions of these templates in the ``democx/templates/django_comments_xtd`` directory to adapt them to the look of the project. Let's create first ``like.html`` with the following content:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}
       {% load comments_xtd %}

       {% block title %}{% trans "Confirm your opinion" %}{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> -
       <a href="{% url 'blog:post_list' %}">Blog</a> -
       <a href="{{ comment.content_object.get_absolute_url }}">{{ comment.content_object }}</a>
       {% endblock %}

       {% block content %}
       <h4 class="page-header text-center">
         {% if already_liked_it %}
         {% trans "You liked this comment, do you want to change it?" %}
         {% else %}
         {% trans "Do you like this comment?" %}
         {% endif %}
       </h4>
       <p class="text-center">{% trans "Please, confirm your opinion on this comment:" %}</p>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           <div class="media">
             <div class="media-left">
               {% if comment.user_url %}
               <a href="{{ comment.user_url }}">
                 {{ comment.user_email|xtd_comment_gravatar }}
               </a>
               {% else %}
               {{ comment.user_email|xtd_comment_gravatar }}
               {% endif %}
             </div>
             <div class="media-body">
               <h6 class="media-heading">
                 {{ comment.submit_date|date:"N j, Y, P" }}&nbsp;-&nbsp;
                 {% if comment.user_url %}
                 <a href="{{ comment.user_url }}" target="_new">{% endif %}
                   {{ comment.user_name }}
                   {% if comment.user_url %}
                 </a>{% endif %}
               </h6>
               <p>{{ comment.comment }}</p>
             </div>
           </div>
           <div class="visible-lg-block visible-md-block">
             <hr/>
           </div>
         </div>
       </div>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           {% if already_liked_it %}
           <div class="alert alert-warning">
             {% trans 'Click on the "withdraw" button if you want to withdraw your positive opinion on this comment.' %} 
           </div>
           {% endif %}
           <div class="well well-lg">
             <form action="." method="post" class="form-horizontal">{% csrf_token %}
               <input type="hidden" name="next" value="{{ comment.get_absolute_url }}">
               <div class="form-group">
                 <div class="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
                   <input type="submit" name="submit" class="btn btn-primary" value="{% if already_liked_it %}{% trans 'Withdraw' %}{% else %}{% trans 'I like it' %}{% endif %}"/>
                   <a class="btn btn-default" href="{{ comment.get_absolute_url }}">{% trans "cancel" %}</a>
                 </div>
               </div>
             </form>
           </div>
         </div>
       </div>
       {% endblock %}
              

And this could be the content for the ``dislike.html`` template:

   .. code-block:: html+django

       {% extends "base.html" %}
       {% load i18n %}
       {% load comments_xtd %}

       {% block title %}{% trans "Confirm your opinion" %}{% endblock %}

       {% block header %}
       <a href="{% url 'homepage' %}">{{ block.super }}</a> -
       <a href="{% url 'blog:post_list' %}">Blog</a> -
       <a href="{{ comment.content_object.get_absolute_url }}">{{ comment.content_object }}</a>
       {% endblock %}

       {% block content %}
       <h4 class="page-header text-center">
         {% if already_disliked_it %}
         {% trans "You didn't like this comment, do you want to change it?" %}
         {% else %}
         {% trans "Do you dislike this comment?" %}
         {% endif %}
       </h4>
       <p class="text-center">{% trans "Please, confirm your opinion on this comment:" %}</p>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           <div class="media">
             <div class="media-left">
               {% if comment.user_url %}
               <a href="{{ comment.user_url }}">
                 {{ comment.user_email|xtd_comment_gravatar }}
               </a>
               {% else %}
               {{ comment.user_email|xtd_comment_gravatar }}
               {% endif %}
             </div>
             <div class="media-body">
               <h6 class="media-heading">
                 {{ comment.submit_date|date:"N j, Y, P" }}&nbsp;-&nbsp;
                 {% if comment.user_url %}
                 <a href="{{ comment.user_url }}" target="_new">{% endif %}
                   {{ comment.user_name }}
                   {% if comment.user_url %}
                 </a>{% endif %}
               </h6>
               <p>{{ comment.comment }}</p>
             </div>
           </div>
           <div class="visible-lg-block visible-md-block">
             <hr/>
           </div>
         </div>
       </div>
       <div class="row">
         <div class="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
           {% if already_liked_it %}
           <div class="alert alert-warning">
             {% trans 'Click on the "withdraw" button if you want to withdraw your negative opinion on this comment.' %} 
           </div>
           {% endif %}
           <div class="well well-lg">
             <form action="." method="post" class="form-horizontal">{% csrf_token %}
               <input type="hidden" name="next" value="{{ comment.get_absolute_url }}">
               <div class="form-group">
                 <div class="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
                   <input type="submit" name="submit" class="btn btn-primary" value="{% if already_liked_it %}{% trans 'Withdraw' %}{% else %}{% trans 'I dislike it' %}{% endif %}"/>
                   <a class="btn btn-default" href="{{ comment.get_absolute_url }}">{% trans "cancel" %}</a>
                 </div>
               </div>
             </form>
           </div>
         </div>
       </div>
       {% endblock %}


One last change we need to do consist in adding the argument ``with_participants`` to the tag :ttag:`get_xtdcomment_tree` in the blog detail template. The immediate effect of this argument is that in addition to the comment and the children of the comment, in each dictionary of the list retrieved by the template tag we will have the list of users who liked the comment and the list of users who disliked it:

   .. code-block:: python

       [
           {
               'comment': comment_object,
               'children': [ list, of, child, comment, dicts ],
               'likedit': [user_who_liked_it_1, user_who_liked_it_2, ...],
               'dislikedit': [user_who_disliked_it_1, user_who_disliked_it_2, ...],
           },
           ...
       ]

Now we have all the changes ready, we can like/dislike comments to see the feature in action.
