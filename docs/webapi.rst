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

As pointed out in the note above, django-comments-xtd notifies receivers of the
signal ``should_request_be_authorized`` to give the request the chance to pass
the `CommentSecurityForm` validation. When a receiver returns ``True``, the form
automatically receives valid values for the ``timestamp`` and ``security_hash``
fields, and the request continues its processing.

These two fields, ``timestamp`` and ``security_hash``, are part of the frontline
against spam in django-comments. In a classic backend driven request-response
cycle these two fields received their values during the GET request, where the
comment form is rendered via the Django template.

However, when using the web API there is no such previous GET request, and thus
both fields can in fact be ignored. In such cases, in order to enable some
sort of spam control, the request can be authenticated via the Django REST
Framework, what in combination of a receiver of the
``should_request_be_authorized`` signal has the effect of **authorizing**
the POST request.


Example of authorization
------------------------

Using the :ref:`example-comp`, in this section we see how to enable posting
comments via the web API.

To start let's see what happens when we try to post a comment. I use the
excellent `HTTPie <https://httpie.org/docs>`_ command line client. Launch
the runserver command in one terminal and try the following in another:

   .. code-block:: bash

    $ http POST http://localhost:8000/comments/api/comment/ \
    > content_type="articles.article" object_pk=1 name="Joe Bloggs" \
    > comment="This is the body of the comment. My opinion on the article." \
    > followup=false reply_to=0 email="joe@bloggs.com" honeypot=""

    HTTP/1.1 400 Bad Request
    Allow: POST, OPTIONS
    Content-Language: en
    Content-Length: 29
    Content-Type: application/json
    Date: Sun, 19 Jul 2020 18:32:46 GMT
    Server: WSGIServer/0.2 CPython/3.8.0
    Vary: Accept, Accept-Language

    [
        "timestamp",
        "security_hash"
    ]

django-comments-xtd is missing the fields ``timestamp`` and ``security_hash``.
Let's add the following code to the comp project...



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
