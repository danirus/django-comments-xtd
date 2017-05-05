import React from 'react';
import ReactDOM from 'react-dom';

import {CommentBox} from './commentbox.jsx';
import {CommentTree} from './commenttree.jsx';


ReactDOM.render(
  React.createElement(CommentTree, window.django_comments_xtd_props),
  document.getElementById('comment-tree')
);
