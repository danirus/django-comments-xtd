import React from 'react';
import ReactDOM from 'react-dom';

import {Comment} from './comment.jsx';


export class CommentTree extends React.Component {
  render() {
    let settings = this.props.settings;
    var nodes = this.props.tree.map(function(item) {
      return (
        <Comment key={item.id} data={item} settings={settings}/>
      );
    });
    return (
      <div className="media-list">
        {nodes}
      </div>
    );
  }
}
