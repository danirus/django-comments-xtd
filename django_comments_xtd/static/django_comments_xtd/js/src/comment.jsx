import $ from 'jquery';
import django from 'django';

import React from 'react';
import ReactDOM from 'react-dom';
import { Remarkable } from 'remarkable';

import { CommentForm } from './commentform.jsx';


function reduce_flags(data, current_user) {
  const flags = {
    like: { active: false, users: [] },
    dislike: { active: false, users: [] },
    removal: { active: false, count: 0 }
  }
  for (const item of data) {
    const user = [item.id, item.user].join(":");
    const active = user === current_user ? true : false;
    if (item.flag === "like") {
      flags.like.users.push(user);
      if (active)
        flags.like.active = active;
    } else if (item.flag === "dislike") {
      flags.dislike.users.push(user);
      if (active)
        flags.dislike.active = active;
    } else if (item.flag === "removal") {
      flags.removal.count += 1;
      if (active)
        flags.removal.active = active;
    }
  }
  return flags;
}


export class Comment extends React.Component {
  constructor(props) {
    super(props);
    const flags = reduce_flags(props.data.flags, props.settings.current_user);
    this.state = {
      current_user: props.settings.current_user,
      removal: flags.removal.active,
      removal_count: flags.removal.count,
      like: flags.like.active,
      like_users: flags.like.users || [],
      dislike: flags.dislike.active,
      dislike_users: flags.dislike.users || [],
      reply_form: {
        component: null,
        is_visible: false
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
      moderator = (
        <span>&nbsp;
        <span className="badge badge-secondary">{label}</span>
        </span>
      );
    }
    return <span>{username}{moderator}</span>;
  }

  _get_right_div_chunk() {
    let flagging_count = "",
        flagging_html = "",
        moderate_html = "",
        url = "";

    if(this.props.data.is_removed)
      return "";

    if(this.props.settings.is_authenticated &&
       this.props.settings.can_moderate &&
       this.state.removal_count > 0)
      {
        let fmts = django.ngettext(
          "%s user has flagged this comment as inappropriate.",
          "%s users have flagged this comment as inappropriate.",
          this.state.removal_count);
        let text = django.interpolate(fmts, [this.state.removal_count]);
        flagging_count = (<span className="badge badge-danger" title={text}>
          {this.state.removal_count}</span>);
      }

    if (this.props.settings.allow_flagging)
      {
        let inapp_msg = "";
        if(this.state.removal) {
          inapp_msg = django.gettext("I flagged it as inappropriate");
          flagging_html = (
            <span>
              {flagging_count}
              <i className="fas fa-flag text-danger" title={inapp_msg}></i>
            </span>
          );
        } else {
          if (this.props.settings.is_authenticated) {
            url = this.props.settings.flag_url.replace('0', this.props.data.id);
          } else {
            url = (this.props.settings.login_url + "?next=" +
                   this.props.settings.flag_url.replace('0', this.props.data.id));
          }
          inapp_msg = django.gettext("flag comment as inappropriate");
          flagging_html = (
            <a className="mutedlink" href={url}>
              <i className="fas fa-flag" title={inapp_msg}></i></a>
          );
        }
      }

    if(this.props.settings.is_authenticated &&
       this.props.settings.can_moderate)
      {
        let remove_msg = django.gettext("remove comment");
        url = this.props.settings.delete_url.replace('0', this.props.data.id);
        moderate_html = (<a className="mutedlink" href={url}>
          <i className="fas fa-trash-alt" title={remove_msg}></i>
        </a>);
      }

    return (<div>{flagging_html} {moderate_html}</div>);
  }

  _get_feedback_chunk(dir) {
    if(!this.props.settings.allow_feedback)
      return "";
    let attr_list = dir + "_users";  // Produce (dis)like_users
    let show_users_chunk = "";

    if(this.props.settings.show_feedback) {
      /* Check whether the user is no longer liking/disliking the comment,
       * and be sure the list of users who liked/disliked the comment
       * is up-to-date likewise.
       */
      let current_user_id = this.state.current_user.split(":")[0];
      let user_ids = this.state[attr_list].map(function(item) {
        return item.split(":")[0];
      });
      if(this.state[dir] &&            // If user expressed opinion, and
         (user_ids.indexOf(current_user_id) == -1)) // user not included.
        {                                       // Append user to the list.
          this.state[attr_list].push(this.state.current_user);
        } else if(!this.state[dir] &&     // If user has no opinion, and
                  (user_ids.indexOf(current_user_id) > -1)) // user included.
          {                                   // Remove the user from the list.
            var pos = user_ids.indexOf(current_user_id);
            this.state[attr_list].splice(pos, 1);
          }

      if(this.state[attr_list].length) {
        let users = this.state[attr_list].map(function(item) {
          return item.split(":")[1];
        });
        users = users.join("<br/>");
        show_users_chunk = (
          <span>&nbsp;<a className="badge badge-primary text-white cfb-counter"
                         data-toggle="tooltip" title={users}>
            {this.state[attr_list].length}
          </a></span>
        );
      }
    }

    let css_class = this.state[dir] ? '' : 'mutedlink';
    let icon = dir == 'like' ? 'thumbs-up' : 'thumbs-down';
    let class_icon = "fas fa-"+icon;
    let click_hdl = dir == 'like' ? this.action_like : this.action_dislike;
    let opinion="", link="#";
    if (dir == 'like')
      opinion = django.gettext('I like it');
    else opinion = django.gettext('I dislike it');

    return (
      <span>{show_users_chunk}&nbsp;<a href="#" onClick={click_hdl}
                                       className={css_class}>
        <i className={class_icon} title={opinion}>
        </i></a>&nbsp;</span>);
  }

  render_feedback_btns() {
    const {
      allow_feedback, who_can_post, is_authenticated
    } = this.props.settings;

    if (allow_feedback) {
      let feedback_id = "feedback-"+this.props.data.id;
      if(this.props.settings.show_feedback)
        this.disposeTooltips(feedback_id);
      let like_feedback = this._get_feedback_chunk("like");
      let dislike_feedback = this._get_feedback_chunk("dislike");
      return (<span id={feedback_id} className="small">{like_feedback}
                <span className="text-muted">|</span>{dislike_feedback}</span>);
    } else
      return null;
  }

  make_form_invisible(submit_status) {
    this.props.on_comment_created();
  }

  handle_reply_click(event) {
    event.preventDefault();
    const { is_authenticated, who_can_post } = this.props.settings;
    if (who_can_post === 'users' && !is_authenticated) {
      return window.location.href = (
        this.props.settings.login_url + "?next=" +
        this.props.settings.reply_url.replace('0', this.props.data.id)
      );
    }
    let component = this.state.reply_form.component;
    let visible = !this.state.reply_form.is_visible;
    if(component == null)
      component = (
        <CommentForm {...this.props.settings}
                     reply_to={this.props.data.id}
                     on_comment_created={this.make_form_invisible.bind(this)} />
      );
    this.setState({reply_form: {component: component, is_visible: visible}});
  }

  _get_reply_link_chunk() {
    const { level } = this.props.data;
    const { max_thread_level } = this.props.settings;
    if (level >= max_thread_level)
      return null;

    let url = this.props.settings.reply_url.replace('0', this.props.data.id),
        reply_label = django.gettext("Reply");

    if(this.props.settings.allow_feedback) {
      return (
        <span>&nbsp;&nbsp;<span className="text-muted">&bull;</span>&nbsp;&nbsp;
          <a className="small mutedlink" href={url}
             onClick={this.handle_reply_click}>{reply_label}</a>
        </span>
      );
    } else {
      return (<a className="small mutedlink" href={url}
              onClick={this.handle_reply_click}>{reply_label}</a>);
    }
  }

  rawMarkup() {
    var md = new Remarkable();
    const rawMarkup = md.render(this.props.data.comment);
    return { __html: rawMarkup };
  }

  render_comment_body() {
    const extra_space = (!this.props.settings.allow_feedback) ? "pb-3" : "";
    if(this.props.data.is_removed) {
      let cls = `text-muted ${extra_space}`;
      return (
        <p className={cls}><em>{this.props.data.comment}</em></p>
      );
    } else {
      let cls = `content ${extra_space}`;
      return (
        <div className={cls} dangerouslySetInnerHTML={this.rawMarkup()}/>
      );
    }
  }

  render_reply_form() {
    if(!this.state.reply_form.is_visible)
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
        this.props.settings.dislike_url.replace('0', this.props.data.id)
      );
  }

  is_hover(elem) {
    return (elem.parentElement.querySelector(':hover') === elem);
  }

  disposeTooltips(feedback_id) {
    // console.log("feedback_id = "+feedback_id);
    var elem = document.getElementById(feedback_id);
    var is_hover = elem && this.is_hover(elem);
    if(elem && !is_hover) {
      $('#'+feedback_id+' A[data-toggle="tooltip"]').tooltip('dispose');
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
      $('#'+feedback_id+' A[data-toggle="tooltip"]').tooltip('dispose');
    }
  }

  render() {
    let comment_id = "c" + this.props.data.id;
    let user_name = this._get_username_chunk();  // Plain name or link.
    let right_div = this._get_right_div_chunk();  // Flagging & moderation.
    let comment_body = this.render_comment_body();
    let feedback_btns = "",
        reply_link = "",
        reply_form = "";
    if (!this.props.data.is_removed) {
      feedback_btns = this.render_feedback_btns();
      reply_link = this._get_reply_link_chunk();
      reply_form = this.render_reply_form();
    }

    var new_label = "";
    if (this.props.newcids.indexOf(this.props.data.id) > -1) {
      new_label = (
        <span>
          <span className="badge badge-success">new</span>&nbsp;-&nbsp;
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
        <img src={this.props.data.user_avatar}
             className="mr-3" height="48" width="48" />
        <div className="media-body">
          <div className="comment pb-3">
            <a name={comment_id}></a>
            <h6 className="mb-1 small d-flex">
              <div className="mr-auto">
                {new_label}{this.props.data.submit_date}&nbsp;-&nbsp;{user_name}
                &nbsp;&nbsp;
                <a className="permalink" href={this.props.data.permalink}>¶</a>
              </div>
              {right_div}
            </h6>
            {comment_body}{feedback_btns}{reply_link}
            {reply_form}
          </div>
          {children}
        </div>
      </div>
    );
  }
}
