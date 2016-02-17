.. _ref-extending:

===============================
Customizing django-comments-xtd
===============================

django-comments-xtd is extendable in the same way as the django-contrib-comments framework. There are only three different details you have to bear in mind:

 1. The setting ``COMMENTS_APP`` must be ``'django_comments_xtd'``.
 2. The setting ``COMMENTS_XTD_MODEL`` must be your model class name, i.e.: ``'mycomments.models.MyComment'``.
 3. The setting ``COMMENTS_XTD_FORM_CLASS`` must be your form class name, i.e.: ``'mycomments.forms.MyCommentForm'``.


In addition to that, write an ``admin.py`` module to see the new comment class in the admin interface. Inherit from ``django_commensts_xtd.admin.XtdCommentsAdmin``. You might want to add your new comment fields to the comment list view, by rewriting the ``list_display`` attribute of your admin class. Or change the details view customizing the ``fieldsets`` attribute.


Custom Comments Demo
====================

The demo site ``custom_comments`` available with the `source code in GitHub <https://github.com/danirus/django-comments-xtd>`_ (directory ``django_comments_xtd\demos\custom_comments``) implements a sample Django project with comments that extend django_comments_xtd with an additional field, a title.


``settings`` Module
-------------------

The ``settings.py`` module contains the following customizations::

  INSTALLED_APPS = (
    # ...
    'django_comments',
    'django_comments_xtd',
    'articles',
    'mycomments',
    # ...
  )

  COMMENTS_APP = "django_comments_xtd"
  COMMENTS_XTD_MODEL = 'mycomments.models.MyComment'
  COMMENTS_XTD_FORM_CLASS = 'mycomments.forms.MyCommentForm'

``models`` Module
-----------------

The new class ``MyComment`` extends django_comments_xtd's ``XtdComment`` with a title field::

  from django.db import models
  from django_comments_xtd.models import XtdComment


  class MyComment(XtdComment):
      title = models.CharField(max_length=256)


``forms`` Module
----------------

The forms module extends ``XtdCommentForm`` and rewrites the method ``get_comment_create_data``::

  from django import forms
  from django.utils.translation import ugettext_lazy as _

  from django_comments_xtd.forms import XtdCommentForm
  from django_comments_xtd.models import TmpXtdComment


  class MyCommentForm(XtdCommentForm):
      title = forms.CharField(
          max_length=256,
          widget=forms.TextInput(attrs={'placeholder': _('title')})
      )

      def get_comment_create_data(self):
          data = super(MyCommentForm, self).get_comment_create_data()
          data.update({'title': self.cleaned_data['title']})
          return data

          
``admin`` Module
----------------

The admin module provides a new class MyCommentAdmin that inherits from XtdCommentsAdmin and customize some of its attributes to include the new field ``title``::

  from django.contrib import admin
  from django.utils.translation import ugettext_lazy as _

  from django_comments_xtd.admin import XtdCommentsAdmin
  from custom_comments.mycomments.models import MyComment


  class MyCommentAdmin(XtdCommentsAdmin):
      list_display = ('thread_level', 'title', 'cid', 'name', 'content_type',
                      'object_pk', 'submit_date', 'followup', 'is_public',
                      'is_removed')
      list_display_links = ('cid', 'title')
      fieldsets = (
          (None,          {'fields': ('content_type', 'object_pk', 'site')}),
          (_('Content'),  {'fields': ('title', 'user', 'user_name', 'user_email', 
                                    'user_url', 'comment', 'followup')}),
          (_('Metadata'), {'fields': ('submit_date', 'ip_address',
                                      'is_public', 'is_removed')}),
      )

  admin.site.register(MyComment, MyCommentAdmin)


Templates
---------

You will need to customize at least the ``comments/list.html`` template to include the ``title`` field in the template.

Also change the template ``comments/form.html`` if you want to customize the way the comment form is displayed.

Both templates belong to the django-contrib-comments application.
