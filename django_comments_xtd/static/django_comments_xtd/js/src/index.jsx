import React from 'react';
import ReactDOM from 'react-dom';

import { App } from './app.jsx';

const rootElement = document.getElementById('comments');
if (!rootElement)
  throw new Error('Failed to find the element with id="comments".');

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App {...{...window.comments_props, ...window.comments_props_override }} />
  </React.StrictMode>
);
