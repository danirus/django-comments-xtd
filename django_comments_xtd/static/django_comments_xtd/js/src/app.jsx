import React, { useReducer } from 'react';

import { InitContext, StateContext } from './context.js';
import { reducer } from './reducer.js';
import { CommentBox } from './commentbox.jsx';

/*
 * props is an object containing all the attributes sent
 * by the get_commentbox_props templatetag (a django-comments-xtd tag).
 * It happens to be the output of the function commentbox_props, in the
 * module django_comments_xtd/frontend.py.
 * Here in JavaScript the structure of the props matches the
 * InitContext, in the context.js module.
 */

export function App(props) {
  const initial_state = {
    tree: [],
    cids: new Set(),
    newcids: new Set(),
    counter: props.comment_count
  }
  const [ state, dispatch ] = useReducer(reducer, initial_state);

  return (
    <StateContext.Provider value={{ state, dispatch }}>
      <InitContext.Provider value={props}>
        <CommentBox />
      </InitContext.Provider>
    </StateContext.Provider>
  )
}
