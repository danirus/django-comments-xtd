# JavaScript Tests

The `js/tests` directory contains a Django project to help with the development of the JavaScript code distributed with django-comments-xtd.

The project provides URLs that are the entry point for the tests. The libraries used for testing are [QUnit](https://qunitjs.com/) and [SinonJS](https://sinonjs.org/).

Continuous Integration tasks are setup with Grunt. See the [gruntfile.cjs](../../gruntfile.cjs), in the root directory of the project.

The command `npm test` runs the code in the `Gruntfile`, which basically runs the `start_server.sh` script, then iterates over the URLs given in the `Gruntfile` to run each of the test specs, and then runs `stop_server.sh`.
