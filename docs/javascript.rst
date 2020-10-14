.. _ref-javascript:

=================
JavaScript plugin
=================

As of version 2.0 django-comments-xtd comes with a JavaScript plugin that
enables comment support as in a Single Page Application fashion. Comments are
loaded and sent in the background, as long as like/dislike opinions. There is
an active verification, based on polling, that checks whether there are new
incoming comments to show to the user, and an update button that allows the
user to refresh the tree, highlighting new comments with a green label to
indicate recently received comment entries.

.. note::

   Future v3 of django-comments-xtd will offer a vanilla JavaScript plugin
   free of frontend choices, to replace the current plugin based on ReactJS,
   jQuery and Twitter-bootstrap.


.. image:: images/update-comment-tree.png

This plugin is done by making choices that might not be the same you made in
your own projects.


Frontend opinions
=================

Django is a backend framework imposing little opinions regarding the frontend.
It merely uses jQuery in the admin site. Nothing more. That leaves developers
the choice to pick anything they want for the frontend to go along with the
backend.

For backend developers the level of stability found in Python and Django
contrasts with the active diversity of JavaScript libraries available for the
frontend.

The JavaScript plugin included in the app is a mix of frontend decisions with
the goal to provide a quick and full frontend solution. Doing so the app is
ready to be plugged in a large number of backend projects, and in a reduced set
of frontend stacks.

The JavaScript Plugin is based on:
 * ReactJS
 * jQuery (merely for Ajax)
 * Remarkable (for Markdown markup support)
 * Twitter-bootstrap (for the UI and the tooltip utility)

The build process is based on Webpack2 instead of any other as good a tool
available in the JavaScript building tools landscape.

The decision of building a plugin based on these choices doesn't mean there
can't be other ones. The project is open to improve its own range of JavaScript
plugins through contributions. If you feel like improving the current plugin or
providing additional ones, please, consider to integrate it using Webpack2 and
try to keep the source code tree as clean and structured as possible.


Build process
=============

In order to further develop the current plugin, fix potential bugs or install
the the plugin from the sources, you have to use `NodeJS
<https://nodejs.org/en/>`_ and `NPM <https://www.npmjs.com/>`_.

Set up the backend
------------------

Before installing the frontend dependencies we will prepare a Python virtualenv
in which we will have all the backend dependencies installed. Let's start by
creating the virtualenv and fetching the sources:

   .. code-block:: shell

       $ virtualenv ~/venv/django-comments-xtd
       $ source ~/venv/django-comments-xtd/bin/activate
       (django-comments-xtd)$ cd ~/src/  # or cd into your sources dir of choice.
       (django-comments-xtd)$ git clone https://github.com/danirus/django-comments-xtd.git
       (django-comments-xtd)$ cd django-comments-xtd
       (django-comments-xtd)$ python setup.py develop

Check whether the app passes the battery of tests:

   .. code-block:: shell

       (django-comments-xtd)$ python setup.py test

As the sample Django project you can use the **comp** example site. Install
first the django-markdown2 package (required by the comp example project) and
setup the project:

   .. code-block:: shell

       (django-comments-xtd)$ cd example/comp
       (django-comments-xtd)$ pip install django-markdown2
       (django-comments-xtd)$ pip install django-rosetta
       (django-comments-xtd)$ python manage.py migrate
       (django-comments-xtd)$ python manage.py loaddata ../fixtures/auth.json
       (django-comments-xtd)$ python manage.py loaddata ../fixtures/sites.json
       (django-comments-xtd)$ python manage.py loaddata ../fixtures/articles.json
       (django-comments-xtd)$ python manage.py runserver

Now the project is ready and the plugin will load from the existing bundle
files. Check it out by visiting an article's page and sending some comments. No
frontend source package has been installed so far.


Install frontend packages
-------------------------

At this point open another terminal and cd into django-comments-xtd source
directory again, then install all the frontend dependencies:

   .. code-block:: shell

       $ cd ~/src/django-comments-xtd
       $ npm install

It will install all the dependencies listed in the **package.json** file in the
local `node_modules` directory. Once it's finished run webpack to build the
bundles and watch for changes in the source tree:

   .. code-block:: shell

       $ webpack --watch

Webpack will put the bundles in the static directory of django-comments-xtd and
Django will fetch them from there when rendering the article's detail page:

   .. code-block:: html+django

       {% block extra-js %}
       [...]
       <script src="{% static 'django_comments_xtd/js/vendor~plugin-3.0.0.js' %}"></script>
       <script src="{% static 'django_comments_xtd/js/plugin-3.0.0.js' %}"></script>
       {% endblock extra-js %}


Code structure
==============

Plugin sources live inside the **static** directory of django-comments-xtd:

   .. code-block:: shell

       $ cd ~/src/django-comments-xtd
       $ tree django_comments_xtd/static/django_comments_xtd/js

       django_comments_xtd/static/django_comments_xtd/js
       ├── src
       │   ├── comment.jsx
       │   ├── commentbox.jsx
       │   ├── commentform.jsx
       │   ├── index.js
       │   └── lib.js
       ├── vendor~plugin-3.0.0.js
       └── plugin-3.0.0.js

       1 directory, 7 files

The intial development was inspired by the `ReactJS Comment Box tutorial
<https://github.com/facebook/react/blob/v15.3.2/docs/docs/tutorial.md>`_.
Component names reflect those of the ReactJS tutorial.

The application entry point is located inside the ``index.js`` file. The
``props`` passed to the **CommentBox** object are those declared in the
``var window.comments_props`` defined in the django template:

   .. code-block:: html+django

       <script>
         window.comments_props = {% get_commentbox_props for object %};
         window.comments_props_override = {
           allow_comments: {%if object.allow_comments%}true{%else%}false{%endif%},
           allow_feedback: true,
           show_feedback: true,
           allow_flagging: true,
           polling_interval: 2000,
         };
       </script>

And are overriden by those declared in the
``var window.comments_props_override``.

To use without the template, you can set up an endpoint to get the props by
generating a view action within the :doc:`webapi`.

Improvements and contributions
==============================

The current ReactJS plugin could be ported to an `Inferno
<https://infernojs.org/>`_ plugin within a reasonable timeframe. Inferno offers
a lighter footprint compared to ReactJS plus it is among the faster JavaScript
frontend frameworks.

Another improvement pending for implementation would be a websocket based
update. At the moment comment updates are received by active polling. See
``commentbox.jsx``, method **load_count** of the **CommentBox** component.

Contributions are welcome, write me an email at mbox@danir.us or open an issue
in the `GitHub repository <https://github.com/danirus/django-comments-xtd>`_.
