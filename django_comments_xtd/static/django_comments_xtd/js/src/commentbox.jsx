import $ from 'jquery';
import md5 from 'md5';
import React from 'react';
import ReactDOM from 'react-dom';
import Remarkable from 'remarkable';

import * as lib from './lib.js';
import {CommentForm} from './commentform.jsx';
import {CommentTree} from './commenttree.jsx';


export class CommentBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      alert: {message: '', cssc: ''},
      previewing: false,
      preview: {name: '', email: '', url: '', comment: ''}
    };
    this.handle_submit = this.handle_submit.bind(this);
    this.handle_preview = this.handle_preview.bind(this);
  }

  handle_submit(data) {
    this.setState({alert: data});
  }
  
  handle_preview(name, email, url, comment) {
    var override = {
      preview: {name: name,
                email: email,
                url: url,
                comment: comment},
      previewing: true
    };
    // var state = Object.assign(this.state, override);
    this.setState(override);
  }

  render_comment_counter() {
    if (this.props.comment_count > 0) {
      var text = "There is one comment below.";
      if(this.props.comment_count > 1)
        text = "There are " + this.props.comment_count + " comments below.";
      return (
        <div>
          <h5 className="text-center">{text}</h5>
          <hr/>
        </div>
      );
    } else
      return "";
  }

  rawMarkup() {
    var md = new Remarkable();
    const rawMarkup = md.render(this.state.preview.comment);
    return { __html: rawMarkup };
  }
  
  render_comment_preview() {
    if(!this.state.previewing)
      return "";
    var media_left = "", heading_name = "";

    // Build Gravatar.
    const hash = md5(this.state.preview.email.toLowerCase());
    const avatar_url = "http://www.gravatar.com/avatar/"+hash+"?s=48&d=mm";
    const avatar_img = <img src={avatar_url} height="48" width="48"/>;
    
    if(this.state.preview.url) {
      media_left = <a href={this.state.preview.url}>{avatar_img}</a>;
      heading_name = (<a href={this.state.preview.url} target="_new">
                      {this.state.preview.name}</a>);
    } else {
      media_left = avatar_img;
      if(this.props.is_authenticated)
        heading_name = this.props.current_user.split(":")[1];
      else heading_name = this.state.preview.name;
    }
    
    return (
      <div>
        <h5 className="text-center">Your comment in preview</h5>
        <div className="media">
          <div className="media-left">{media_left}</div>
          <div className="media-body">
            <h6 className="media-heading">Now&nbsp;-&nbsp;{heading_name}</h6>
            <p dangerouslySetInnerHTML={this.rawMarkup()} />
          </div>
        </div>
        <hr/>
      </div>
    );
  }

  render_comment_form() {
    if(this.props.allow_comments) {
      let alert_div = "";
      let settings = {send_url: this.props.send_url,
                      is_authenticated: this.props.is_authenticated};
      if(this.state.alert.message) {
        alert_div = (
          <div className={this.state.alert.cssc}>
            {this.state.alert.message}
          </div>
        );
      }
      return (
        <div className="comment">
          <h4 className="text-center">Post your comment</h4>
          {alert_div}
          <div className="well well-lg">
            <CommentForm form={this.props.form} settings={settings}
                         onCommentSubmit={this.handle_submit}
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
