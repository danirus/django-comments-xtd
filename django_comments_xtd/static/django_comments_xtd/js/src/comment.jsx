import $ from 'jquery';
import django from 'django';

import React from 'react';
import ReactDOM from 'react-dom';
import Remarkable from 'remarkable';

import {CommentForm} from './commentform.jsx';


export class Comment extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      current_user: props.settings.current_user,
      removal: props.data.flags.removal.active,
      removal_count: props.data.flags.removal.count,
      like: props.data.flags.like.active,
      like_users: props.data.flags.like.users || [],
      dislike: props.data.flags.dislike.active,
      dislike_users: props.data.flags.dislike.users || [],
      reply_form: {
        component: null,
        show: false
      }
    };
    this.action_like = this.action_like.bind(this);
    this.action_dislike = this.action_dislike.bind(this);
    this.handle_reply_click = this.handle_reply_click.bind(this);
  }
  
  _get_username_chunk() {
    let username = this.props.data.user_name, moderator = "";

    if(this.props.data.user_url && !this.props.data.is_removed)
      username = <a href={this.props.data.user_url}>{username}</a>;

    if(this.props.data.user_moderator) {
      var label = django.gettext("moderator");
      moderator = (<span>
                   &nbsp;<span className="label label-default">{label}</span>
                   </span>);
    }
    return <span>{username}{moderator}</span>;
  }

  _get_right_div_chunk() {
    let flagging_html = "", moderate_html = "", url = "";

    if(this.props.data.is_removed)
      return "";
    
    if (this.props.settings.allow_flagging)
    {
      var inappropriate_msg = "";
      if(this.state.removal) {
        inappropriate_msg = django.gettext("I flagged it as inappropriate");
        flagging_html = (
          <span className="glyphicon glyphicon-flag text-danger"
                title={inappropriate_msg}>
          </span>
        );
      } else {
        if (this.props.settings.is_authenticated) {
          url = this.props.settings.flag_url.replace('0', this.props.data.id);
        } else {
          url = (this.props.settings.login_url + "?next=" +
                 this.props.settings.flag_url.replace('0', this.props.data.id));
        }
        inappropriate_msg = django.gettext("flag comment as inappropriate");
        flagging_html = (
          <a className="mutedlink" href={url}>
            <span className="glyphicon glyphicon-flag"
                  title={inappropriate_msg}></span>
          </a>);
      }
    }
    
    if(this.props.settings.is_authenticated &&
       this.props.settings.can_moderate)
    {
      var remove_msg = django.gettext("remove comment");
      url = this.props.settings.delete_url.replace('0', this.props.data.id);
      moderate_html = (
        <a className="mutedlink" href={url}>
          <span className="glyphicon glyphicon-trash" title={remove_msg}>
          </span>
        </a>);
      if(this.state.removal_count>0) {
        var fmts = django.ngettext(
          "%s user has flagged this comment as inappropriate.",
          "%s users have flagged this comment as inappropriate.",
          this.state.removal_count);
        var text = django.interpolate(fmts, [this.state.removal_count]);
        moderate_html = (
          <span>
            {moderate_html}&nbsp;
            <span className="label label-warning" title={text}>
              {this.state.removal_count}</span>
          </span>
        );
      }
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
    let attr_list = dir + "_users";  // Produce (dis)like_users

    let show_users_chunk = "";
    if(this.props.settings.show_feedback) {

      // Check whether the user is no longer liking/disliking the comment,
      // and be sure the list list of users who liked/disliked the comment
      // is up-to-date likewise.
      let current_user_id = this.state.current_user.split(":")[0];
      let user_ids = this.state[attr_list].map(function(item) {
        return item.split(":")[0];
      });
      if(this.state[dir] &&       // If user expressed opinion, and
         (user_ids.indexOf(current_user_id) == -1)) // user is not included.
      { // Append user to the list.
        this.state[attr_list].push(this.state.current_user);
      } else if(!this.state[dir] && // If user doesn't have an opinion
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

    var css_class = this.state[dir] ? '' : 'mutedlink';
    var icon = dir == 'like' ? 'thumbs-up' : 'thumbs-down';
    var class_icon = "small glyphicon glyphicon-"+icon;
    var click_hdl = dir == 'like' ? this.action_like : this.action_dislike;
    var opinion="", link="#";
    if (dir == 'like')
      opinion = django.gettext('I like it');
    else opinion = django.gettext('I dislike it');

    return (
      <span>
        {show_users_chunk}  <a href="#" onClick={click_hdl}
                               className={css_class}>
          <span className={class_icon} title={opinion}></span>
        </a>
      </span>
    );
  }

  render_feedback_btns() {
    if(this.props.settings.allow_feedback)
    {
      let feedback_id = "feedback-"+this.props.data.id;
      if(this.props.settings.show_feedback)
        this.destroyTooltips(feedback_id);
      let like_feedback = this._get_feedback_chunk("like");
      let dislike_feedback = this._get_feedback_chunk("dislike");
      return (
        <span id={feedback_id} className="small">
          {like_feedback}
          <span className="text-muted"> | </span>
          {dislike_feedback}
        </span>
      );
    } else
      return "";
  }
  
  handle_reply_click(event) {
    event.preventDefault();
    var component = this.state.reply_form.component;
    var visible = !this.state.reply_form.show;
    if(component==null) 
      component = (
        <CommentForm form={this.props.settings.form}
                     reply_to={this.props.data.id}
                     send_url={this.props.settings.send_url}
                     current_user={this.props.settings.current_user}
                     is_authenticated={this.props.settings.is_authenticated}
                     request_name={this.props.settings.request_name}
                     request_email_address={this.props.settings.request_email_address}
                     on_comment_created={this.props.on_comment_created} />
      );
    this.setState({reply_form: {component: component,
                                show: visible}});
  }

  _get_reply_link_chunk() {
    if(!this.props.data.allow_reply)
      return "";
    
    let separator = "";
    if(this.props.settings.allow_feedback)
      separator = <span className="text-muted">&bull;</span>;
    let url = this.props.settings.reply_url.replace('0', this.props.data.id);
    let reply_label = django.gettext("Reply");
    
    return (
      <span>&nbsp;&nbsp;{separator}&nbsp;&nbsp;
        <a className="small mutedlink" href={url}
           onClick={this.handle_reply_click}>{reply_label}</a>
      </span>
    );
  }

  rawMarkup() {
    var md = new Remarkable();
    const rawMarkup = md.render(this.props.data.comment);
    return { __html: rawMarkup };
  }
  
  render_comment_body() {  
    if(this.props.data.is_removed)
      return (
        <p className="text-muted"><em>{this.props.data.comment}</em></p>
      );
    else
      return (
        <div className="content" dangerouslySetInnerHTML={this.rawMarkup()}/>
      );
  }

  render_reply_form() {
    if(!this.state.reply_form.show)
      return "";
    return (
      <div>{this.state.reply_form.component}</div>
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
            this.setState({like: true, dislike: false});
          else if(flag=='dislike')
            this.setState({dislike: true, like: false});
        }.bind(this),
        204: function() {
          if(flag=='like')
            this.setState({like: false});
          else if(flag=='dislike')
            this.setState({dislike: false});
        }.bind(this)
      },
      error: function(xhr, status, err) {
        debugger;
        if(xhr.status==400 && xhr.responseJSON.non_field_errors.length)
          alert(xhr.responseJSON.non_field_errors[0]);
        else
          console.error(this.props.settings.feedback_url, status,
                        err.toString());
      }.bind(this)
    });
  }

  action_like(event) {
    event.preventDefault();
    if(this.props.settings.is_authenticated)
      return this._post_feedback('like');
    else
      return window.location.href = (
        this.props.settings.login_url + "?next=" +
        this.props.settings.like_url.replace('0', this.props.data.id)
      );
  }

  action_dislike(event) {
    event.preventDefault();
    if(this.props.settings.is_authenticated)
      return this._post_feedback('dislike');
    else
      return window.location.href = (
        this.props.settings.login_url + "?next=" +
        this.props.settings.dislike_url.replace('0', this.props.id)
      );
  }

  is_hover(elem) {
    return (elem.parentElement.querySelector(':hover') === elem);
  }

  destroyTooltips(feedback_id) {
    // console.log("feedback_id = "+feedback_id);
    var elem = document.getElementById(feedback_id);
    var is_hover = elem && this.is_hover(elem);
    if(elem && !is_hover) {
      $('#'+feedback_id+' A[data-toggle="tooltip"]').tooltip('destroy');
    }
  }
  
  componentDidMount() {
    var feedback_id = "feedback-" + this.props.data.id;
    var options = {html: true, selector: '.cfb-counter'};
    $('#'+feedback_id).tooltip(options);
  }

  componentDidUpdate() {
    var feedback_id = "feedback-" + this.props.data.id;
    var options = {html: true, selector: '.cfb-counter'};
    $('#'+feedback_id).tooltip(options);
  }
  
  componentWillUnmount() {
    var feedback_id = "feedback-" + this.props.data.id;
    var elem = document.getElementById(feedback_id);
    var is_hover = elem && this.is_hover(elem);
    if(elem && !is_hover) {
      $('#'+feedback_id+' A[data-toggle="tooltip"]').tooltip('destroy');
    }
  }
  
  render() {
    var user_name = this._get_username_chunk();  // Plain name or link.
    var right_div = this._get_right_div_chunk();  // Flagging & moderation.
    var comment_body = this.render_comment_body();
    var feedback_btns = this.render_feedback_btns();
    var reply_link = this._get_reply_link_chunk();
    var comment_id = "c" + this.props.data.id;
    var reply_form = this.render_reply_form();

    var new_label = "";
    if (this.props.newcids.indexOf(this.props.data.id) > -1) {
      new_label = (
        <span>
          <span className="label label-success">new</span>&nbsp;-&nbsp;
        </span>
      );
    }
    
    var children = "";
    var settings = this.props.settings;
    if (this.props.data.children != null) {
      children = this.props.data.children.map(function(item) {
        return (
          <Comment key={item.id}
                   data={item}
                   settings={settings}
                   newcids={this.props.newcids}
                   on_comment_created={this.props.on_comment_created} />
        );
      }.bind(this));
    }
    
    return (
      <div className="media" id={comment_id}>
        <div className="media-left">
          <img src={this.props.data.user_avatar} height="48" width="48" />
        </div>
        <div className="media-body">
          <div className="comment">
            <h6 className="media-heading">
              {new_label}{this.props.data.submit_date} - {user_name}
              &nbsp;&nbsp;
              <a className="permalink" href={this.props.data.permalink}>¶</a>
              {right_div}
            </h6>
            <a name={comment_id}></a>
            {comment_body}{feedback_btns}{reply_link}
            {reply_form}
          </div>
          {children}
        </div>
      </div>
    );
  }
}
