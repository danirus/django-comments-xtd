import React from 'react';
import ReactDOM from 'react-dom';

import {CommentBox} from './commentbox.jsx';
import {CommentTree} from './commenttree.jsx';


ReactDOM.render(
  React.createElement(CommentTree,
                      Object.assign(window.comments_props,
                                    window.comments_props_override)),
  document.getElementById('comment-tree')
);
