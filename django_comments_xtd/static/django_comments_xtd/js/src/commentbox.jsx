import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

import * as lib from './lib.js';
import {Comment} from './comment.jsx';
import {CommentForm} from './commentform.jsx';


export class CommentBox extends React.Component {
  constructor(props) {
    super(props);
    lib.jquery_ajax_setup('csrftoken');
    this.state = {
      previewing: false,
      preview: {name: '', email: '', url: '', comment: ''},
      tree: []
    };
    this.handle_comment_created = this.handle_comment_created.bind(this);
    this.handle_preview = this.handle_preview.bind(this);
  }

  handle_comment_created() {
    this.loadComments();
  }
  
  handle_preview(name, email, url, comment) {
    this.setState({
      preview: {name: name, email: email, url: url, comment: comment},
      previewing: true
    });
  }

  reset_preview() {
    this.setState({
      preview: {name: '', email: '', url: '', comment: ''},
      previewing: false
    });
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

  render_comment_form() {
    if(this.props.allow_comments) {
      return (
        <CommentForm form={this.props.form}
                     send_url={this.props.send_url}
                     is_authenticated={this.props.is_authenticated}
                     on_comment_created={this.handle_comment_created} />
      );
    } else {
      return (
        <h5>Comments are disabled for this article.</h5>
      );
    }
  }

  create_tree(data) {
    let tree = new Array();
    let order = new Array();
    let comments = {};
    let children = {};

    function get_children(cid) {
      return children[cid].map(function(index) {
        if(comments[index].children == undefined) {
          comments[index].children = get_children(index);
        }
        return comments[index];
      });
    };
    
    for (let item of data) {
      comments[item.id] = item;
      if(item.level == 0) {
        order.push(item.id);
      }
      children[item.id] = [];
      if(item.parent_id!==item.id) {
        children[item.parent_id].push(item.id);
      }
    }
    for (let cid of order) {
      comments[cid].children = get_children(cid);
      tree.push(comments[cid]);
    }

    this.setState({tree:tree});
  }
  
  loadComments() {
    $.ajax({
      url: this.props.list_url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.create_tree(data);
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.list_url, status, err.toString());
      }.bind(this)
    });
  }
  
  componentDidMount() {
    this.loadComments();
  }
  
  render() {
    var settings = this.props;
    var comment_counter = this.render_comment_counter();
    var comment_form = this.render_comment_form();

    var nodes = this.state.tree.map(function(item) {
      return (
        <Comment key={item.id}
                 data={item}
                 settings={settings}
                 on_comment_created={this.handle_comment_created} />
      );
    }.bind(this));
    
    return (
      <div>
        {comment_counter}
        {comment_form}
        <hr/>
        <div className="comment-tree">
          <div className="media-list">
            {nodes}
          </div>
        </div>
      </div>
    );
  }
}
