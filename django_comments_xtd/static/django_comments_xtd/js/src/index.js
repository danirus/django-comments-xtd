import React from 'react';
import ReactDOM from 'react-dom';

import { CommentBox } from './commentbox.jsx';


ReactDOM.render(
  React.createElement(CommentBox,
                      Object.assign(window.comments_props,
                                    window.comments_props_override)),
  document.getElementById('comments')
);
