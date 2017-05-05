import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

import * as lib from './lib.js';
import {Comment} from './comment.jsx';


export class CommentTree extends React.Component {
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
      },
      tree: []
    };
  }

  createTree(data) {
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
  
  componentDidMount() {
    $.ajax({
      url: this.props.list_url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.createTree(data);
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.list_url, status, err.toString());
      }.bind(this)
    });
  }
  
  render() {
    var settings = this.state.settings;
    var nodes = this.state.tree.map(function(item) {
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
