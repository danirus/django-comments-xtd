import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

class CommentForm extends React.Component {
  render() {
    return (
      <form method="POST" action="" className="form-horizontal">
      </form>
    );
  }
}


class Comment extends React.Component {
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
    if(!this.props.settings.allow_feedback ||
       !this.props.settings.is_authenticated)
      return "";

    let show_users_chunk = "";
    if(this.props.settings.show_feedback) {
      let attr_users = dir + "dit_users";  // Produce (dis)likedit_users
      if(this.props.data[attr_users].length) {
        let users = this.props.data[attr_users].join("<br/>");
        show_users_chunk = (
          <a data-toggle="tooltip" title={users}>
            <span className="small">
              {this.props.data[attr_users].length}
            </span>
          </a>
        );
      }
    }
    
    let attr_bool = "i" + dir + "dit";
    let css_class = this.props.data[attr_bool] ? '' : 'mutedlink';
    let icon = dir == 'like' ? 'thumbs-up' : 'thumbs-down';
    let class_icon = "small glyphicon glyphicon-"+icon;
    return (
      <span>
        {show_users_chunk}  <a href="#" className={css_class}>
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
    if(this.props.settings.allow_feedback &&
       this.props.settings.is_authenticated)
    {
      let like_feedback = this._get_feedback_chunk("like");
      let dislike_feedback = this._get_feedback_chunk("dislike");
      feedback = (
        <span className="small">
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

  componentDidMount() {
    let comment_id = "c" + this.props.data.id;
    $('#'+comment_id+' A[data-toggle="tooltip"]').tooltip({html:true});
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
        is_authenticated: this.props.is_authenticated || false,
        allow_feedback: this.props.allow_feedback || false,
        show_feedback: this.props.show_feedback || false,
        allow_flagging: this.props.allow_flagging || false,
        can_moderate: this.props.can_moderate || false
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
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.createTree(data);
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
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
