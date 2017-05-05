import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

import * as lib from './lib.js';


export class CommentBox extends React.Component {
  constructor(props) {
    super(props);
    lib.jquery_ajax_setup('csrftoken');
    this.state = {
      settings: {
        current_user: this.props.current_user || "0:Anonymous",
        is_authenticated: this.props.is_authenticated || false,
        allow_feedback: this.props.allow_feedback || false,
        show_feedback: this.props.show_feedback || false,
        allow_flagging: this.props.allow_flagging || false,
        can_moderate: this.props.can_moderate || false,
        feedback_url: this.props.feedback_url,
        delete_url: this.props.delete_url,
        reply_url: this.props.reply_url,
        flag_url: this.props.flag_url
      }
    };
  }

  _get_comment_counter_block() {
    if (this.props.comment_count > 0) {
      var text = "There is one comment below.";
      if(this.props.comment_count > 1)
        text = "There are " + this.props.comment_count + " comments below.";
      return (
        <span>
          <H5 className="text-center">{text}</H5>
          <hr/>
        </span>
      );
    } else
      return "";
  }

  _get_form_block() {
    if(this.props.allow_comments) {
    } else {
      return (
        <h5>Comments are disabled for this article.</h5>
      );
    }
  }
  
  render() {
    var settings = this.state.settings;
    var comment_counter = this._get_comment_counter_block();
    var form_block = this._get_form_block();
    return (
      <div id="comments">
        {comment_counter}
        {form_block}
      </div>
    );
  }
}
