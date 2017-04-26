import React from 'react';
import ReactDOM from 'react-dom';


class CommentTree extends React.Component {
  render() {
    var allow_feedback = this.props.allow_feedback ? "Allow" : "Disallow";
    return (
      <ul className="media-list">
        <li className="media"><a href="{props.api_url}">Enlace</a></li>
        <li className="media">{allow_feedback}</li>
      </ul>
    );
  }
}

ReactDOM.render(
  React.createElement(CommentTree, window.django_comments_xtd_props),
  document.getElementById('comment-tree')
);
