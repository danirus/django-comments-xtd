.. _ref-webapi:

=======
Web API
=======

.. _django-rest-framework: http://www.django-rest-framework.org/

django-comments-xtd uses django-rest-framework_ to expose a Web API that provides developers with access to the same functionalities offered through the web user interface. The Web API has been designed to cover the needs required by the :doc:`javascript`, and it's open to grow in the future to cover additional functionalities.

There are 5 methods available to perform the following actions:

 #. Post a new comment.
 #. Retrieve the list of comments posted to a given content type and object ID.
 #. Retrieve the number of comments posted to a given content type and object ID.
 #. Post user's like/dislike feedback.
 #. Post user's removal suggestions.

Finally there is the ability to generate a view action in ``django_comments_xtd.api.frontend`` to return the commentbox props as used by the :doc:`javascript` plugin for use with an existing `django-rest-framework <http://www.django-rest-framework.org/>`_ project.

.. contents:: Table of Contents
   :depth: 1
   :local:


Post a new comment
==================

 | URL name: **comments-xtd-api-create**
 | Mount point: **<comments-mount-point>/api/comment/**
 | HTTP Methods: POST
 | HTTP Responses: 201, 202, 204, 403
 | Serializer: ``django_comments_xtd.api.serializers.WriteCommentSerializer``

This method expects the same fields submitted in a regular django-comments-xtd
form. The serializer uses the function ``django_comments.get_form`` to verify
data validity.

Meaning of the HTTP Response codes:

 * **201**: Comment created.
 * **202**: Comment in moderation.
 * **204**: Comment confirmation has been sent by mail.
 * **403**: Comment rejected, as in :ref:`disallow`.

.. note::

   Up until v2.6 fields ``timestamp`` and ``security_hash``, related with the
   `CommentSecurityForm <https://django-contrib-comments.readthedocs.io/en/latest/forms.html?highlight=commentsecurityform#django_comments.forms.CommentSecurityForm>`_, had to be provided in the post request. As of v2.7 it is possible to use
   a django-rest-framework's authentication class in combination with
   django-comments-xtd's signal ``should_request_be_authorized``
   (:ref:`signal-and-receiver-label`) to automatically pass the
   CommentSecurityForm validation.


Authorize the request
---------------------

As pointed out in the note above, django-comments-xtd notifies receivers of the signal ``should_request_be_authorized`` to give the request the chance to pass the `CommentSecurityForm` validation. When a receiver returns ``True``, the form automatically receives valid values for the ``timestamp`` and ``security_hash`` fields, and the request continues its processing.

These two fields, ``timestamp`` and ``security_hash``, are part of the frontline against spam in django-comments. In a classic backend driven request-response cycle these two fields received their values during the GET request, where the comment form is rendered via the Django template.

However, when using the web API there is no such previous GET request, and thus both fields can in fact be ignored. In such cases, in order to enable some sort of spam control, the request can be authenticated via the Django REST Framework, what in combination with a receiver of the ``should_request_be_authorized`` signal has the effect of **authorizing** the POST request.


Example of authorization
------------------------

In this section we go through the changes that will enable posting comments via the web API in the :ref:`example-simple`. We have to:

 1. Modify the settings module.
 2. Modify the urls module to allow login and logout via DRF's api-auth.
 3. Create a new authentication class, in this case it will be an authentication scheme based on DRF's `Custom authentication <https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication>`_, but you could use any other one.
 4. Create a new receiver function for the signal ``should_request_be_authorized``.
 5. Post a test comment as a visitor.
 6. Post a test comment as a signed in user.

Modify the settings module
**************************

We will modify the ``simple/settings.py`` module to add ``rest_framework`` to ``INSTALLED_APPS``. In addition we will create a custom setting that will be used later in the receiver function for the signal ``should_request_be_authorized``. I call the setting ``MY_DRF_AUTH_TOKEN``. And we will also add Django Rest Framework settings to enable request authentication.

Append the code to your ``simple/settings.py`` module:

   .. code-block:: python

      INSTALLED_APPS = [
         ...
         'rest_framework',
         'simple.articles',
         ...
      ]

      # import os, binascii; binascii.hexlify(os.urandom(20)).decode()
      MY_DRF_AUTH_TOKEN = "08d9fd42468aebbb8087b604b526ff0821ce4525"

      REST_FRAMEWORK = {
          'DEFAULT_AUTHENTICATION_CLASSES': [
              'rest_framework.authentication.SessionAuthentication',
              'simple.apiauth.APIRequestAuthentication'
         ]
      }

Modify the urls module
**********************

In order to send comments as a logged in user we will first login using the end point provided by Django REST Framework's urls module. Append the following to the ``urlpatterns`` in ``simple/urls.py``:

.. code-block:: python

   urlpatterns = [
       ...

       re_path(r'^api-auth/', include('rest_framework.urls',
                                      namespace='rest_framework')),
   ]


Create a new authentication class
*********************************

In this step we create a class to validate that the request has a valid Authorization header. We follow the instructions about how to create a `Custom authentication <https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication>`_ scheme in the Django REST Framework documentation.

In the particular case of this class we don't want to authenticate the user but merely the request. To authenticate the user we added the class ``rest_framework.authentication.SessionAuthentication`` to the **DEFAULT_AUTHENTICATION_CLASSES** of the **REST_FRAMEWORK** setting. So once we read the auth token we will return a tuple with an **AnonymousUser** instance and the content of the token read.

Create the module ``simple/apiauth.py`` with the following content:

   .. code-block:: python

      from django.contrib.auth.models import AnonymousUser

      from rest_framework import HTTP_HEADER_ENCODING, authentication, exceptions


      class APIRequestAuthentication(authentication.BaseAuthentication):
          def authenticate(self, request):
              auth = request.META.get('HTTP_AUTHORIZATION', b'')
              if isinstance(auth, str):
                  auth = auth.encode(HTTP_HEADER_ENCODING)

              pieces = auth.split()
              if not pieces or pieces[0].lower() != b'token':
                  return None

              if len(pieces) == 1:
                  msg = _("Invalid token header. No credentials provided.")
                  raise exceptions.AuthenticationFailed(msg)
              elif len(pieces) > 2:
                  msg = _("Invalid token header."
                          "Token string should not contain spaces.")
                  raise exceptions.AuthenticationFailed(msg)

              try:
                  auth = pieces[1].decode()
              except UnicodeError:
                  msg = _("Invalid token header. "
                      "Token string should not contain invalid characters.")

              return (AnonymousUser(), auth)

The class doesn't validate the token. We will do it with the receiver function in the next section.

Create a receiver for ``should_request_be_authorized``
******************************************************

Now let's create the receiver function. The receiver function will be called when the comment is posted, from the validate method of the **WriteCommentSerializer**. If the receiver returns True the request is considered authorized.

Append the following code to the ``simple/articles/models.py`` module:

   .. code-block:: python

      from django.conf import settings
      from django.dispatch import receiver
      from django_comments_xtd.signals import should_request_be_authorized

      [...]

      @receiver(should_request_be_authorized)
      def my_callback(sender, comment, request, **kwargs):
          if (
              (request.user and request.user.is_authenticated) or
              (request.auth and request.auth == settings.MY_DRF_AUTH_TOKEN)
          ):
              return True

The left part of the *if* is True when the ``rest_framework.authentication.SessionAuthentication`` recognizes the user posting the comment as a signed in user. However if the user sending the comment is a mere visitor and the request contains a valid **Authorization** token, then our class ``simple.apiauth.APIRequestAuthentication`` will have put the auth token in the request. If the auth token contains the value given in the setting **MY_DRF_AUTH_TOKEN** we can considered the request authorized.

Post a test comment as a visitor
********************************

Now with the previous changes in place launch the Django development server and let's try to post a comment using the web API.

These are the fields that have to be sent:

 * **content_type**: A string with the content_type ie: ``content_type="articles.article"``.
 * **object_pk**: The object ID we are posting the comment to.
 * **name**: The name of the person posting the comment.
 * **email**: The email address of the person posting the comment. It's required when the comment has to be confirmed via email.
 * **followup**: Boolean to indicate whether the user wants to receive follow-up notification via email.
 * **reply_to**: When threading is enabled, reply_to is the comment ID being responded with the comment being sent. If comments are not threaded the reply_to must be 0.
 * **comment**: The content of the comment.

I will use the excellent `HTTPie <https://httpie.org/docs>`_ command line client:

   .. code-block:: bash

    $ http POST http://localhost:8000/comments/api/comment/ \
           'Authorization:Token 08d9fd42468aebbb8087b604b526ff0821ce4525' \
           content_type="articles.article" object_pk=1 name="Joe Bloggs" \
           followup=false reply_to=0 email="joe@bloggs.com" \
           comment="This is the body, the actual comment..."

    HTTP/1.1 204 No Content
    Allow: POST, OPTIONS
    Content-Length: 2
    Content-Type: application/json
    Date: Fri, 24 Jul 2020 20:06:02 GMT
    Server: WSGIServer/0.2 CPython/3.8.0
    Vary: Accept

Check that in the terminal where you are running ``python manage.py runserver`` you have got the content of the mail message that would be sent to **joe@bloggs.com**. Copy the confirmation URL and visit it to confirm the comment.

Post a test comment as a signed in user
***************************************

To post a comment as a logged in user we first have to obtain the csrftoken:

   .. code-block:: bash

    $ http localhost:8000/api-auth/login/ --session=session1 -h

    HTTP/1.1 200 OK
    Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private
    Content-Length: 4253
    Content-Type: text/html; charset=utf-8
    Date: Fri, 24 Jul 2020 21:00:35 GMT
    Expires: Fri, 24 Jul 2020 21:00:35 GMT
    Server: WSGIServer/0.2 CPython/3.8.0
    Server-Timing: SQLPanel_sql_time;dur=0;desc="SQL 0 queries"
    Set-Cookie: csrftoken=nEJczcG2M3LrcxIKiHbkxDFy2gmplPtn87pAFhp0CQz47TvZ58v8S2eCpWD9Zadm; expires=Fri, 23 Jul 2021 21:00:35 GMT; Max-Age=31449600; Path=/; SameSite=Lax
    Vary: Cookie

Copy the value of csrftoken and attach it to the login HTTP request:

   .. code-block:: bash

    $ http -f POST localhost:8000/api-auth/login/ username=admin password=admin \
              X-CSRFToken:nEJczcG2M3LrcxIKiHbkxDFy2gmplPtn87pAFhp0CQz47TvZ58v8S2eCpWD9Zadm \
              --session=session1

    HTTP/1.1 302 Found
    Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private
    Content-Length: 0
    Content-Type: text/html; charset=utf-8
    Date: Fri, 24 Jul 2020 21:06:11 GMT
    Expires: Fri, 24 Jul 2020 21:06:11 GMT
    Location: /accounts/profile/
    Server: WSGIServer/0.2 CPython/3.8.0
    Set-Cookie: csrftoken=z3FtVTPWudwYrWrqSQLOb2HZ0JNAmoA3P8M4RSDhTtJr7LrSVVAbfDp847Xetuwm; expires=Fri, 23 Jul 2021 21:06:11 GMT; Max-Age=31449600; Path=/; SameSite=Lax
    Set-Cookie: sessionid=iyq0q9kqxhjwsgnq95taqbdw2p35v4jb; expires=Fri, 07 Aug 2020 21:06:11 GMT; HttpOnly; Max-Age=1209600; Path=/; SameSite=Lax
    Vary: Cookie


Finally send the comment with the new csrftoken:

   .. code-block:: bash

    $ http POST http://localhost:8000/comments/api/comment/ \
                content_type="articles.article" object_pk=1 followup=false \
                reply_to=0 comment="This is the body, the actual comment..." \
                name="Administrator" email="admin@example.com" \
                X-CSRFToken:z3FtVTPWudwYrWrqSQLOb2HZ0JNAmoA3P8M4RSDhTtJr7LrSVVAbfDp847Xetuwm \
                --session=session1

    HTTP/1.1 201 Created
    Allow: POST, OPTIONS
    Content-Length: 282
    Content-Type: application/json
    Date: Fri, 24 Jul 2020 21:06:58 GMT
    Server: WSGIServer/0.2 CPython/3.8.0
    Vary: Accept, Cookie

    {
        "comment": "This is the body, the actual comment...",
        "content_type": "articles.article",
        "email": "admin@example.com",
        "followup": false,
        "honeypot": "",
        "name": "Administrator",
        "object_pk": "1",
        "reply_to": 0,
        "security_hash": "9da968a7ff000f2bd4aa1a669bb70d18934be574",
        "timestamp": "1595624818"
    }

The comment must be already listed in the page, sent as the user ``admin``.


Retrieve comment list
=====================

 | URL name: **comments-xtd-api-list**
 | Mount point: **<comments-mount-point>/api/<content-type>/<object-pk>/**
 |        <content-type> is a hyphen separated lowecase pair app_label-model
 |        <object-pk> is an integer representing the object ID.
 | HTTP Methods: GET
 | HTTP Responses: 200
 | Serializer: ``django_comments_xtd.api.serializers.ReadCommentSerializer``

This method retrieves the list of comments posted to a given content type and object ID:

   .. code-block:: bash

       $ http http://localhost:8000/comments/api/blog-post/4/

       HTTP/1.0 200 OK
       Allow: GET, HEAD, OPTIONS
       Content-Length: 2707
       Content-Type: application/json
       Date: Tue, 23 May 2017 11:59:09 GMT
       Server: WSGIServer/0.2 CPython/3.6.0
       Vary: Accept, Cookie
       X-Frame-Options: SAMEORIGIN

       [
           {
               "allow_reply": true,
               "comment": "Integer erat leo, ...",
               "flags": [
                   {
                       "flag": "like",
                       "id": 1,
                       "user": "admin"
                   },
                   {
                       "flag": "like",
                       "id": 2,
                       "user": "fulanito"
                   },
                   {
                       "flag": "removal",
                       "id": 2,
                       "user": "fulanito"
                   }
               ],
               "id": 10,
               "is_removed": false,
               "level": 0,
               "parent_id": 10,
               "permalink": "/comments/cr/8/4/#c10",
               "submit_date": "May 18, 2017, 9:19 AM",
               "user_avatar": "http://www.gravatar.com/avatar/7dad9576 ...",
               "user_moderator": true,
               "user_name": "Joe Bloggs",
               "user_url": ""
           },
           {
               ...
           }
       ]


Retrieve comments count
=======================

 | URL name: **comments-xtd-api-count**
 | Mount point: **<comments-mount-point>/api/<content-type>/<object-pk>/count/**
 |        <content-type> is a hyphen separated lowecase pair app_label-model
 |        <object-pk> is an integer representing the object ID.
 | HTTP Methods: GET
 | HTTP Responses: 200
 | Serializer: ``django_comments_xtd.api.serializers.ReadCommentSerializer``

This method retrieves the number of comments posted to a given content type and object ID:

   .. code-block:: bash

       $ http http://localhost:8000/comments/api/blog-post/4/count/

       HTTP/1.0 200 OK
       Allow: GET, HEAD, OPTIONS
       Content-Length: 11
       Content-Type: application/json
       Date: Tue, 23 May 2017 12:06:38 GMT
       Server: WSGIServer/0.2 CPython/3.6.0
       Vary: Accept, Cookie
       X-Frame-Options: SAMEORIGIN

       {
           "count": 4
       }


Post like/dislike feedback
==========================

 | URL name: **comments-xtd-api-feedback**
 | Mount point: **<comments-mount-point>/api/feedback/**
 | HTTP Methods: POST
 | HTTP Responses: 201, 204, 403
 | Serializer: ``django_comments_xtd.api.serializers.FlagSerializer``

This method toggles flags like/dislike for a comment. Successive calls set/unset the like/dislike flag:

   .. code-block:: bash

       $ http -a admin:admin POST http://localhost:8000/comments/api/feedback/ comment=10 flag="like"

       HTTP/1.0 201 Created
       Allow: POST, OPTIONS
       Content-Length: 34
       Content-Type: application/json
       Date: Tue, 23 May 2017 12:27:00 GMT
       Server: WSGIServer/0.2 CPython/3.6.0
       Vary: Accept, Cookie
       X-Frame-Options: SAMEORIGIN

       {
           "comment": 10,
           "flag": "I liked it"
       }

Calling it again unsets the *"I liked it"* flag:

   .. code-block:: bash

       $ http -a admin:admin POST http://localhost:8000/comments/api/feedback/ comment=10 flag="like"

       HTTP/1.0 204 No Content
       Allow: POST, OPTIONS
       Content-Length: 0
       Date: Tue, 23 May 2017 12:26:56 GMT
       Server: WSGIServer/0.2 CPython/3.6.0
       Vary: Accept, Cookie
       X-Frame-Options: SAMEORIGIN

It requires the user to be logged in:

   .. code-block:: bash

       $ http POST http://localhost:8000/comments/api/feedback/ comment=10 flag="like"

       HTTP/1.0 403 Forbidden
       Allow: POST, OPTIONS
       Content-Length: 58
       Content-Type: application/json
       Date: Tue, 23 May 2017 12:27:31 GMT
       Server: WSGIServer/0.2 CPython/3.6.0
       Vary: Accept, Cookie
       X-Frame-Options: SAMEORIGIN

       {
           "detail": "Authentication credentials were not provided."
       }


Post removal suggestions
========================

 | URL name: **comments-xtd-api-flag**
 | Mount point: **<comments-mount-point>/api/flag/**
 | HTTP Methods: POST
 | HTTP Responses: 201, 403
 | Serializer: ``django_comments_xtd.api.serializers.FlagSerializer``

This method sets the *removal suggestion* flag on a comment. Once created for a given user successive calls return 201 but the flag object is not created again.

   .. code-block:: bash

       $ http POST http://localhost:8000/comments/api/flag/ comment=10 flag="report"

       HTTP/1.0 201 Created
       Allow: POST, OPTIONS
       Content-Length: 42
       Content-Type: application/json
       Date: Tue, 23 May 2017 12:35:02 GMT
       Server: WSGIServer/0.2 CPython/3.6.0
       Vary: Accept, Cookie
       X-Frame-Options: SAMEORIGIN

       {
           "comment": 10,
           "flag": "removal suggestion"
       }

As the previous method, it requires the user to be logged in.
