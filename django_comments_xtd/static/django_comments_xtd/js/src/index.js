import React from 'react';
import ReactDOM from 'react-dom';

import { App } from './app.jsx';

const root = ReactDOM.createRoot(document.getElementById('comments'));
root.render(
  React.createElement(App,
    Object.assign(window.comments_props, window.comments_props_override)
  )
);
