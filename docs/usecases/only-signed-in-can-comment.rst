.. _ref-recipe-only-signed-in-can-comment:

================================
Only signed in users can comment
================================

Setup your Django project so that django-comments-xtd will allow only signed in users to post comments.

 * commentbox.jsx control whether the user in the session can post comments or not. If she cannot, we inform the user of such a condition. There are two ways to inform the user:
    1. We display a hardcoded message provided within the JavaScript Plugin. Specifically in the function render_comment_form of the commentbox.jsx module.
    1. We load an HTML element with a given ID and display it using the dangerouslySetInnerHTML. The HTML element is loaded in the article_detail.html via a templatetag. The templatetag will add the HTML element with an ID that changes when the page is reloaded. The ID is generated using a function that is also used by the frontend.py's commentsbox_props function. Doing so when the page reloads, both, the HTML Element with the customized message loaded via the templatetag, and the props passed to the JavaScript plugin, will use the same ID. Thus the JavaScript plugin will know what ID to load. In order to produce the same ID I have to use middleware, so that I store it in the session and I fetch it from there.

