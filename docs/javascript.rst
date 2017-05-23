.. _ref-javascript:

=================
JavaScript plugin
=================

As of version 2.0 django-comments-xtd comes with a JavaScript plugin that enables comment support as in a Single Page Application fashion. Comments are loaded and sent in the background, as long as like/dislike opinions. There is an active verification, based on polling, that checks whether there are new incoming comments to show to the user, and an update button that allows the user to refresh the tree, highlighting new comments with a green label to indicate recently received comment entries.

.. image:: images/update-comment-tree.png

This plugin is done by making choices that might not be the same you made in your own projects.

           
Frontend opinions
=================

Django is a backend framework imposing little opinions regarding the frontend. It merely uses jQuery in the admin site. Nothing more. That leaves developers the choice to pick anything they want for the frontend to go along with the backend.

For backend developers the level of stability found in Python and Django contrasts with the active diversity of JavaScript libraries available for the frontend.

The JavaScript plugin included in the app is a mix of frontend decisions with the goal to provide a quick and full frontend solution. Doing so the app is ready to be plugged in a large number of backend projects, and in a reduced set of frontend stacks.

The JavaScript Plugin is based on:
 * ReactJS
 * jQuery (merely for Ajax)
 * Remarkable (for Markdown markup support)
 * Twitter-bootstrap (for the UI and the tooltip utility)

The build process is based on Webpack2 instead of any other as good a tool available in the JavaScript building tools landscape.

The decision of building a plugin based on these choices doesn't mean there can't be other ones. The project is open to improve its own range of JavaScript plugins through contributions. If you feel like improving the current plugin or providing additional ones, please, consider to integrate it using Webpack2 and try to keep the source code tree as clean and structured as possible.


Build process
=============

In order to further develop the current plugin, fix potential bugs or install the the plugin from the sources, you have to use `NodeJS <https://nodejs.org/en/>`_ and `NPM <https://www.npmjs.com/>`_.

Before installing the frontend dependencies we will prepare a Python virtualenv in which we will have all the backend dependencies installed. Create the virtualenv and fetch the sources:

   .. code-block:: shell

       $ virtualenv ~/venv/django-comments-xtd
       $ source ~/venv/django-comments-xtd/bin/activate
       (django-comments-xtd)$ git clone https://github.com/danirus/django-comments-xtd.git
       (django-comments-xtd)$ python setup.py develop
       
                          

Code structure
==============

Write about the source code tree and the generated files.

ReactJS code
------------

Write about the design decisions made while writing the plugin.


Improvements and contributions
==============================

Build an Inferno plugin.
Add support for websockets instead of polling.
