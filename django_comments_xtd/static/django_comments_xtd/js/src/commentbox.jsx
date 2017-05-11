import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

import * as lib from './lib.js';
import {CommentForm} from './commentform.jsx';
import {CommentTree} from './commenttree.jsx';


export class CommentBox extends React.Component {
  constructor(props) {
    super(props);
  //   lib.jquery_ajax_setup('csrftoken');
    // this.state = {
    //   settings: {
    //     current_user: this.props.current_user || "0:Anonymous",
    //     is_authenticated: this.props.is_authenticated || false,
    //     allow_flagging: this.props.allow_flagging || false,
    //     allow_feedback: this.props.allow_feedback || false,
    //     show_feedback: this.props.show_feedback || false,
    //     can_moderate: this.props.can_moderate || false,
    //     feedback_url: this.props.feedback_url,
    //     delete_url: this.props.delete_url,
    //     reply_url: this.props.reply_url,
    //     flag_url: this.props.flag_url,
    //     list_url: this.props.list_url,
    //     send_url: this.props.send_url,
    //     form: this.props.form
    //   }
    // };
    this.state = {
      previewing: false,
      preview: {
        name: '',
        email: '',
        url: '',
        comment: ''
      }
    };
  }

  handle_preview(name, email, url, comment) {
    this.setState({preview: {name: name,
                             email: email,
                             url: url,
                             comment: comment},
                   previewing: true});
  }

  render_comment_counter() {
    if (this.props.comment_count > 0) {
      var text = "There is one comment below.";
      if(this.props.comment_count > 1)
        text = "There are " + this.props.comment_count + " comments below.";
      return (
        <span>
          <h5 className="text-center">{text}</h5>
          <hr/>
        </span>
      );
    } else
      return "";
  }

  render_comment_preview() {
  }

  render_comment_form() {
    if(this.props.allow_comments) {
      let settings = {send_url: this.props.send_url,
                      is_authenticated: this.props.is_authenticated};
      return (
        <div className="comment">
          <h4 className="text-center">Post your comment.</h4>
          <div className="well well-lg">
            <CommentForm form={this.props.form} settings={settings}
                         onCommentPreview={this.handle_preview} />
          </div>
        </div>
      );
    } else {
      return (
        <h5>Comments are disabled for this article.</h5>
      );
    }
  }
  
  render() {
    var settings = this.props;
    var comment_counter = this.render_comment_counter();
    var comment_preview = this.render_comment_preview();
    var comment_form = this.render_comment_form();
    return (
      <div>
        {comment_counter}
        {comment_preview}
        {comment_form}
        <hr/>
        <div className="comment-tree">
          <CommentTree settings={settings}/>
        </div>
      </div>
    );
  }
}
