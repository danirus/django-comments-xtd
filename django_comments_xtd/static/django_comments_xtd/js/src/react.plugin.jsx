import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

import * as lib from './local-lib.js';


$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!lib.csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", lib.getCookie('csrftoken'));
    }
  }
});


class CommentForm extends React.Component {
  render() {
    return (
      <form method="POST" action="" className="form-horizontal">
      </form>
    );
  }
}


class Comment extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      current_user: props.settings.current_user,
      ilikedit: props.data.ilikedit,
      idislikedit: props.data.idislikedit,
      likedit_users: props.data.likedit_users,
      dislikedit_users: props.data.dislikedit_users      
    };
    this.actionLike = this.actionLike.bind(this);
    this.actionDislike = this.actionDislike.bind(this);
  }
  
  _get_username_chunk() {
    let username = this.props.data.user_name, moderator = "";

    if(this.props.data.user_url && !this.props.data.is_removed)
      username = <a href={this.props.data.user_url}>{username}</a>;

    if(this.props.data.is_moderator)
      moderator = (<span>
                   &nbsp;<span className="label label-default">moderator</span>
                   </span>);
    
    return <span>{username}{moderator}</span>;
  }

  _get_right_div_chunk() {
    let flagging_html = "", moderate_html = "";

    if(this.props.data.is_removed)
      return "";
    
    if(this.props.settings.is_authenticated &&
       this.props.settings.allow_flagging)
    {
      flagging_html = (
        <a className="mutedlink" href="#">
          <span className="glyphicon glyphicon-flag" title="flag comment">
          </span>
        </a>);
    }
    
    if(this.props.settings.is_authenticated &&
       this.props.settings.can_moderate)
    {
      moderate_html = (
        <a className="mutedlink" href="#">
          <span className="glyphicon glyphicon-trash" title="remove comment">
          </span>
        </a>);
    }
    
    return (
      <p className="pull-right">
        {flagging_html} {moderate_html}
      </p>
    );
  }

  _get_feedback_chunk(dir) {
    if(!this.props.settings.allow_feedback)
      return "";

    let attr_opinion = "i" + dir + "dit";
    let attr_list = dir + "dit_users";  // Produce (dis)likedit_users

    let show_users_chunk = "";
    if(this.props.settings.show_feedback) {
      // Check whether the user is no longer liking/disliking the comment,
      // and be sure the list list of users who liked/disliked the comment
      // is up-to-date likewise.
      let current_user_id = this.state.current_user.split(":")[0];
      let user_ids = this.state[attr_list].map(function(item) {
        return item.split(":")[0];
      });
      if(this.state[attr_opinion] &&       // If user expressed opinion, and
         (user_ids.indexOf(current_user_id) == -1)) // user is not included.
      { // Append user to the list.
        this.state[attr_list].push(this.state.current_user);
      } else if(!this.state[attr_opinion] && // If user doesn't have an opinion
                (user_ids.indexOf(current_user_id) > -1)) // user is included.
      { // Remove the user from the list.
        var pos = user_ids.indexOf(current_user_id);
        this.state[attr_list].splice(pos, 1);
      }
      
      if(this.state[attr_list].length) {
        let users = this.state[attr_list].map(function(item) {
          return item.split(":")[1];
        });
        users = users.join("<br/>");
        show_users_chunk = (
          <a className="cfb-counter" data-toggle="tooltip" title={users}>
            <span className="small">
              {this.state[attr_list].length}
            </span>
          </a>
        );
      }
    }
    let css_class = this.state[attr_opinion] ? '' : 'mutedlink';
    let icon = dir == 'like' ? 'thumbs-up' : 'thumbs-down';
    let class_icon = "small glyphicon glyphicon-"+icon;
    let click_hdl = dir == 'like' ? this.actionLike : this.actionDislike;
    return (
      <span>
        {show_users_chunk}  <a href="#" onClick={click_hdl}
                               className={css_class}>
          <span className={class_icon}></span>
        </a>
      </span>
    );
  }
  
  _get_reply_link_chunk() {
    if(this.props.data.reply_url==null)
      return "";
    
    let separator = "";
    if(this.props.settings.allow_feedback)
      separator = <span className="text-muted">&bull;</span>;

    return (
      <span>&nbsp;&nbsp;{separator}&nbsp;&nbsp;
        <a className="small mutedlink"
           href={this.props.data.reply_url}>Reply</a>
      </span>
    );
  }
  
  _get_comment_p_chunk() {
    if(this.props.data.is_removed)
      return (
        <p className="text-muted">
          <em>{this.props.data.comment}</em>
        </p>
      );

    let feedback = "";
    if(this.props.settings.allow_feedback)
    {
      let feedback_id = "feedback-"+this.props.data.id;
      if(this.props.settings.show_feedback)
        this.destroyTooltips(feedback_id);
      let like_feedback = this._get_feedback_chunk("like");
      let dislike_feedback = this._get_feedback_chunk("dislike");
      feedback = (
        <span id={feedback_id} className="small">
          {like_feedback}
          <span className="text-muted"> | </span>
          {dislike_feedback}
        </span>
      );
    }

    let reply_link = this._get_reply_link_chunk();
    return (
      <p>
        {this.props.data.comment}
        <br/>
        {feedback}{reply_link}
      </p>
    );
  }

  _post_feedback(flag) {
    $.ajax({
      method: 'POST',
      url: this.props.settings.feedback_url,
      data: {comment: this.props.data.id, flag: flag},
      dataType: 'json',
      cache: false,
      statusCode: {
        201: function() {
          let state = {};
          if(flag=='like')
            this.setState({ilikedit: true, idislikedit: false});
          else if(flag=='dislike')
            this.setState({idislikedit: true, ilikedit: false});
        }.bind(this),
        204: function() {
          if(flag=='like')
            this.setState({ilikedit: false});
          else if(flag=='dislike')
            this.setState({idislikedit: false});
        }.bind(this)
      },
      error: function(xhr, status, err) {
        console.error(this.props.settings.feedback_url, status, err.toString());
      }.bind(this)
    });
  }

  actionLike(event) {
    event.preventDefault();
    return this._post_feedback('like');
  }

  actionDislike(event) {
    event.preventDefault();
    return this._post_feedback('dislike');
  }

  destroyTooltips(feedback_id) {
    $('#'+feedback_id+' A[data-toggle="tooltip"]').tooltip('destroy');
  }
  
  componentDidMount() {
    let feedback_id = "feedback-" + this.props.data.id;
    let options = {html: true, selector: '.cfb-counter'};
    $('#'+feedback_id).tooltip(options);
  }

  componentDidUpdate() {
    let feedback_id = "feedback-" + this.props.data.id;
    let options = {html: true, selector: '.cfb-counter'};
    $('#'+feedback_id).tooltip(options);
  }
  
  componentWillUnmount() {
    let feedback_id = "feedback-" + this.props.data.id;
    $('#'+feedback_id+' A[data-toggle="tooltip"]').tooltip('destroy');
  }
  
  render() {
    let user_name = this._get_username_chunk();  // Plain name or link.
    let right_div = this._get_right_div_chunk();  // Flagging & moderation.
    let comment_p = this._get_comment_p_chunk();
    let comment_id = "c" + this.props.data.id;
    
    let children = "";
    let settings = this.props.settings;
    if (this.props.data.children != null) {
      children = this.props.data.children.map(function(item) {
        return (
          <Comment key={item.id} data={item} settings={settings}/>
        );
      });
    }

    return (
      <div className="media" id={comment_id}>
        <div className="media-left">
          <img src={this.props.data.avatar} height="48" width="48" />
        </div>
        <div className="media-body">
          <div className="comment">
            <h6 className="media-heading">
              {this.props.data.submit_date} - {user_name}
              &nbsp;&nbsp;
              <a className="permalink" href={this.props.data.permalink}>¶</a>
              {right_div}
            </h6>
            {comment_p}
            <a name={comment_id}></a>
          </div>
          {children}
        </div>
      </div>
    );
  }
}


class CommentTree extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      settings: {
        current_user: this.props.current_user || "0:Anonymous",
        is_authenticated: this.props.is_authenticated || false,
        allow_feedback: this.props.allow_feedback || false,
        show_feedback: this.props.show_feedback || false,
        allow_flagging: this.props.allow_flagging || false,
        can_moderate: this.props.can_moderate || false,
        feedback_url: this.props.feedback_url,
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


ReactDOM.render(
  React.createElement(CommentTree, window.django_comments_xtd_props),
  document.getElementById('comment-tree')
);
