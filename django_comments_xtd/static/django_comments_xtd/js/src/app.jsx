import React, { useReducer } from 'react';

import { InitContext, StateContext } from './context.js';
import { reducer } from './reducer.js';
import { CommentBox } from './commentbox.jsx';


export function App(props) {
  const initial_state = {
    tree: [],
    cids: [],
    newcids: [],
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
