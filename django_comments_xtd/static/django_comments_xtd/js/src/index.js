import React from 'react';
import ReactDOM from 'react-dom';

import { App } from './app.jsx';

function execute_xtd() {
  var comments = document.querySelectorAll('#comments, .comments');
  var props = '';
  if (typeof window.comments_props != "undefined") {
    props = Object.assign(window.comments_props, window.comments_props_override);
  }
  if (NodeList.prototype.isPrototypeOf(comments)) {
    comments.forEach(async (item) => {
      if (item.getAttribute('data-comments-added') == null) {
        item.setAttribute('data-comments-added', true);
        var _props = props;
        if (item.querySelector('.comments-props') != null) {
          _props = JSON.parse(item.querySelector('.comments-props').getAttribute('data-comments'));
        }
        const root = ReactDOM.createRoot(item);
        root.render(
          React.createElement(App, _props)
        )
      }
    });
  }
}

// https://stackoverflow.com/a/61511955/1902215
function waitForElm(selector) {
  return new Promise(resolve => {
    if (document.querySelector(selector)) {
      return resolve(document.querySelector(selector));
    }

    const observer = new MutationObserver(mutations => {
      if (document.querySelector(selector)) {
        observer.disconnect();
        resolve(document.querySelector(selector));
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  });
}

execute_xtd();

waitForElm('#comments, .comments').then((elm) => {
  execute_xtd();
});
