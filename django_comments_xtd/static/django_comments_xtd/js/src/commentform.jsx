import React from 'react';
import ReactDOM from 'react-dom';


export class CommentForm extends React.Component {
  render() {
    return (
      <form method="POST" action={this.props.settings.list_url}
            className="form-horizontal">
        <fieldset>
          <div className="alert alert-danger hidden"
               data-comment-element="errors"></div>
        </fieldset>
      </form>
    );
  }
}
