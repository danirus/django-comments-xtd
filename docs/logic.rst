.. _ref-logic:

=============
Control Logic
=============

Following is the application control logic described in 4 actions:

1. The user visits a page that accepts comments. Your app or a 3rd. party app handles the request:
 
 a. Your template shows content that accepts comments. It loads the ``comments`` templatetag and using tags as ``render_comment_list`` and ``render_comment_form`` the template shows the current list of comments and the *post your comment* form.

2. The user **clicks on preview**. Django Comments Framework ``post_comment`` view handles the request:

 a. Renders ``comments/preview.html`` either with the comment preview or with form errors if any.

3. The user **clicks on post**. Django Comments Framework ``post_comment`` view handles the request:

 a. If there were form errors it does the same as in point 2. 

 b. Otherwise creates an instance of ``TmpXtdComment`` model: an in-memory representation of the comment.

 c. Send signal ``comment_will_be_posted`` and ``comment_was_posted``. The *django-comments-xtd* receiver ``on_comment_was_posted`` receives the second signal with the ``TmpXtdComment`` instance and does as follows:

  * If the user is authenticated or confirmation by email is not required (see :doc:`settings`):

   * An instance of ``XtdComment`` hits the database.

   * An email notification is sent to previous comments followers telling them about the new comment following up theirs. Comment followers are those who ticked the box *Notify me about follow up comments via email*.

   * Otherwise a confirmation email is sent to the user with a link to confirm the comment. The link contains a secured token with the ``TmpXtdComment``. See below :ref:`the-secure-token-label`.

 d. Pass control to the ``next`` parameter handler if any, or render the ``comments/posted.html`` template:

  * If the instance of ``XtdComment`` has already been created, redirect to the the comments's absolute URL.

  * Otherwise the template content should inform the user about the confirmation request sent by email.

4. The user **clicks on the confirmation link**, in the email message. *Django-comments-xtd* ``confirm`` view handles the request:

 a. Checks the secured token in the URL. If it's wrong returns a 404 code.
 
 b. Otherwise checks whether the comment was already confirmed, in such a case returns a 404 code.

 c. Otherwise sends a ``confirmation_received`` signal. You can register a receiver to this signal to do some extra process before approving the comment. See :ref:`signal-and-receiver-label`. If any receiver returns False the comment will be rejected and the template ``django_comments_xtd/discarded.html`` will be rendered.

 d. Otherwise an instance of ``XtdComment`` finally hits the database, and

 e. An email notification is sent to previous comments followers telling them about the new comment following up theirs.


.. _the-secure-token-label:
     

Creating the secure token for the confirmation URL
--------------------------------------------------

The Confirmation URL sent by email to the user has a secured token with the comment. To create the token Django-comments-xtd uses the module ``signed.py`` authored by Simon Willison and provided in `Django-OpenID <http://github.com/simonw/django-openid>`_. 

``django_openid.signed`` offers two high level functions:

* **dumps**: Returns URL-safe, sha1 signed base64 compressed pickle of a given object.

* **loads**: Reverse of dumps(), raises ValueError if signature fails.

A brief example::

    >>> signed.dumps("hello")
    'UydoZWxsbycKcDAKLg.QLtjWHYe7udYuZeQyLlafPqAx1E'

    >>> signed.loads('UydoZWxsbycKcDAKLg.QLtjWHYe7udYuZeQyLlafPqAx1E')
    'hello'

    >>> signed.loads('UydoZWxsbycKcDAKLg.QLtjWHYe7udYuZeQyLlafPqAx1E-modified')
    BadSignature: Signature failed: QLtjWHYe7udYuZeQyLlafPqAx1E-modified


There are two components in dump's output ``UydoZWxsbycKcDAKLg.QLtjWHYe7udYuZeQyLlafPqAx1E``, separatad by a '.'. The first component is a URLsafe base64 encoded pickle of the object passed to dumps(). The second component is a base64 encoded hmac/SHA1 hash of "$first_component.$secret".

Calling signed.loads(s) checks the signature BEFORE unpickling the object -this protects against malformed pickle attacks. If the signature fails, a ValueError subclass is raised (actually a BadSignature).


.. index::
   single: Signal; Receiver

.. _signal-and-receiver-label:

Signal and receiver
===================

In addition to the `signals sent by the Django Comments Framework <https://docs.djangoproject.com/en/1.3/ref/contrib/comments/signals/>`_, django-comments-xtd sends the following signal:

 * **confirmation_received**: Sent when the user clicks on the confirmation link and before the ``XtdComment`` instance is created in the database.

 * **comment_thread_muted**: Sent when the user clicks on the mute link, in a follow-up notification.


Sample use of the ``confirmation_received`` signal
--------------------------------------------------

You might want to register a receiver for ``confirmation_received``. An example function receiver could check the time stamp in which a user submitted a comment and the time stamp in which the confirmation URL has been clicked. If the difference between them is over 7 days we will discard the message with a graceful `"sorry, it's a too old comment"` template.

Extending the demo site with the following code will do the job:

   .. code-block:: python
  
       #----------------------------------------
       # append the below code to demos/simple/views.py:

       from datetime import datetime, timedelta
       from django_comments_xtd import signals

       def check_submit_date_is_within_last_7days(sender, data, request, **kwargs):
           plus7days = timedelta(days=7)
	       if data["submit_date"] + plus7days < datetime.now():
	           return False
           signals.confirmation_received.connect(check_submit_date_is_within_last_7days)
    
    
       #-----------------------------------------------------
       # change get_comment_create_data in django_comments_xtd/forms.py to cheat a
       # bit and make Django believe that the comment was submitted 7 days ago:

       def get_comment_create_data(self):
	       from datetime import timedelta                                     # ADD THIS

           data = super(CommentForm, self).get_comment_create_data()
           data['followup'] = self.cleaned_data['followup']
           if settings.COMMENTS_XTD_CONFIRM_EMAIL:
               # comment must be verified before getting approved
               data['is_public'] = False
               data['submit_date'] = datetime.datetime.now() - timedelta(days=8)  # ADD THIS
           return data


Try the simple demo site again and see that the `django_comments_xtd/discarded.html` template is rendered after clicking on the confirmation URL.


.. index::
   single: Level
   pair: Thread; Level
   pair: Maximum; Thread
   triple: Maximum; Thread; Level

Maximum Thread Level
====================

Nested comments are disabled by default, to enable them use the following settings:

 * ``COMMENTS_XTD_MAX_THREAD_LEVEL``: an integer value
 * ``COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL``: a dictionary

Django-comments-xtd inherits the flexibility of `django-contrib-comments framework <https://docs.djangoproject.com/en/1.4/ref/contrib/comments/>`_, so that developers can plug it to support comments on as many models as they want in their projects. It is as suitable for one model based project, like comments posted to stories in a simple blog, as for a project with multiple applications and models.

The configuration of the maximum thread level on a simple project is done by declaring the ``COMMENTS_XTD_MAX_THREAD_LEVEL`` in the ``settings.py`` file:

   .. code-block:: python

       COMMENTS_XTD_MAX_THREAD_LEVEL = 2


Comments then could be nested up to level 2:

   .. code-block:: text

       <In an instance detail page that allows comments>

       First comment (level 0)
         |-- Comment to First comment (level 1)
           |-- Comment to Comment to First comment (level 2)

Comments posted to instances of every model in the project will allow up to level 2 of threading.

On a project that allows users posting comments to instances of different models, the developer may want to declare a maximum thread level on a per ``app.model`` basis. For example, on an imaginary blog project with stories, quotes, diary entries and book/movie reviews, the developer might want to define a default, project wide, maximum thread level of 1 for any model and an specific maximum level of 5 for stories and quotes:

   .. code-block:: python

       COMMENTS_XTD_MAX_THREAD_LEVEL = 1
       COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {
           'blog.story': 5,
           'blog.quote': 5,
       }

So that ``blog.review`` and ``blog.diaryentry`` instances would support comments nested up to level 1, while ``blog.story`` and ``blog.quote`` instances would allow comments nested up to level 5.
