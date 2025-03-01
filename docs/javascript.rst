.. _ref-javascript:

=================
JavaScript plugin
=================

django-comments-xtd comes with a JavaScript plugin. When using the plugin comments are loaded and sent in the background, as well as like/dislike feedback. The plugin checks whether there are new incoming comments, and shows an update button that allows the user to refresh the comment tree. When the refresh takes place new comments are highlighted with a green label.

.. cs_image:: images/update-comment-tree.png
    :width: 95%
    :align: center
    :class: border-radius-1

Frontend Stack
==============

The JavaScript Plugin is based on:

* Bootstrap
* ReactJS
* Remarkable (for Markdown markup support)

They are all external dependencies that have to be included as ``<script>`` elements in your templates (see demo sites' ``base.html`` template).

The build process uses:

* `rollup.js`_ to create the JavaScript plugin file.
* `terser`_ to minimize the JavaScript plugin.

Build process
=============

In order to further develop the current plugin, fix potential bugs or install
the plugin from the sources, you have to use `NodeJS
<https://nodejs.org/en/>`_ and `NPM <https://www.npmjs.com/>`_.

Set up the backend
------------------

Before installing the frontend dependencies prepare the backend development environment:

.. code-block:: shell

    git clone https://github.com/danirus/django-comments-xtd.git
    cd django-comments-xtd
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
    pip install -r requirements_tests.pip

Check whether the app passes the battery of tests:

.. code-block:: shell

    python -m pytest -x

As the sample Django project you can use the **comp** example site. Install
first the django-markdown2 package (required by the comp example project) and
setup the project:

.. code-block:: shell

    cd example/comp
    pip install django-markdown2
    pip install django-rosetta
    python manage.py migrate
    python manage.py loaddata ../fixtures/auth.json
    python manage.py loaddata ../fixtures/sites.json
    python manage.py loaddata ../fixtures/articles.json
    python manage.py loaddata ../fixtures/quotes.json
    python manage.py runserver

Now the project is ready and the plugin will load from the existing bundle
files. Check it out by visiting an article's page and sending some comments. No
frontend source package has been installed so far.


Install frontend packages
-------------------------

At this point open another terminal and cd into django-comments-xtd source
directory again, then install all the frontend dependencies:

.. code-block:: shell

    cd ~/src/django-comments-xtd
    npm install

It will install all the dependencies listed in the **package.json** file in the
local `node_modules` directory. Once it's finished run webpack to build the
bundles and watch for changes in the source tree:

.. code-block:: shell

       npm run compile

Rollup puts the bundle in the static directory of django-comments-xtd and
Django will fetch it from there when rendering the article's detail page:

.. code-block:: html+django

    {% block extra-js %}
    [...]
    <script src="{% static 'django_comments_xtd/js/django-comments-xtd-2.10.4.js' %}"></script>
    {% endblock extra-js %}

Code structure
==============

Plugin sources live inside the **static** directory of django-comments-xtd:

.. code-block:: shell

    cd ~/src/django-comments-xtd
    tree django_comments_xtd/static/django_comments_xtd/js

Which results in:

.. code-block::

    django_comments_xtd/static/django_comments_xtd/js
    ├── src
    │   ├── app.js
    │   ├── comment.jsx
    │   ├── commentbox.jsx
    │   ├── commentform.jsx
    │   ├── index.js
    │   └── lib.js
    ├── tests
    │   ├── comment.test.jsx
    │   ├── commentform.test.jsx
    │   ├── reducer.test.jsx
    │   └── lib.test.js
    ├── django-comments-xtd-2.10.4.js
    └── django-comments-xtd-2.10.4.min.js

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
``window.comments_props_override``.

To use without the template, you can set up an endpoint to get the props by
generating a view action within the :doc:`webapi`.

Comment design
==============

.. code-block:: text

  photo  | Header content                           | flags
         |-------------------------------------------------
         | Comment text that can take several lines all
         | together... blah blah blah...
         |-------------------------------------------------
         | Footer content
         |-------------------------------------------------
         | Nested comments...

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

.. _rollup.js: https://rollupjs.org/
.. _terser: https://terser.org/
.. _sass: https://sass-lang.com/
.. _clean-css-cli: https://www.npmjs.com/package/clean-css-cli