import django from 'django';
import React, { useContext, useEffect, useState } from 'react';
import { Remarkable } from 'remarkable';

import { getCookie } from './lib.js';
import { InitContext, StateContext } from './context.js';
import { CommentForm } from './commentform.jsx';


function reduce_flags(data, current_user) {
  const flags = {
    like: { is_active: false, users: [] },
    dislike: { is_active: false, users: [] },
    removal: { is_active: false, count: 0 }
  }
  for (const item of data) {
    const user = [item.id, item.user].join(":");
    const is_active = user === current_user ? true : false;
    switch (item.flag) {
      case "like": {
        flags.like.users.push(user);
        flags.like.is_active = is_active;
      }
      case "dislike": {
        flags.dislike.users.push(user);
        flags.dislike.is_active = is_active;
      }
      case "removal": {
        flags.removal.count += 1;
        flags.removal.is_active = is_active;
      }
    }
  }
  return flags;
}


export function Comment({data, onCommentCreated}) {
  const {
    children,
    comment,
    id,
    is_removed,
    level,
    permalink,
    submit_date,
    user_avatar,
    user_moderator,
    user_name,
    user_url,

  } = data;

  const {
    allow_feedback,
    allow_flagging,
    can_moderate,
    current_user,
    delete_url,
    dislike_url,
    feedback_url,
    flag_url,
    is_authenticated,
    like_url,
    login_url,
    max_thread_level,
    reply_url,
    show_feedback,
    who_can_post
  } = useContext(InitContext);

  const { state } = useContext(StateContext);
  const { newcids } = state;

  const { flags } = data;
  const _flags = reduce_flags(flags, current_user);

  const [lstate, setLstate] = useState({
    current_user: current_user,
    removal: _flags.removal.is_active,
    removal_count: _flags.count,
    like: _flags.like.is_active,
    like_users: _flags.like.users || [],
    dislike: _flags.dislike.is_active,
    dislike_users: _flags.dislike.users || [],
    reply_form: {
      component: undefined,
      is_visible: false
    }
  });

  const get_username_chunk = () => {
    let
      username = user_name,
      moderator = "";

    if (user_url && !is_removed) {
      username = (
        <a
          href={data.user_url}
          className="text-decoration-none"
        >{username}</a>
      );
    }

    if (user_moderator) {
      const label = django.gettext("moderator");
      moderator = (
        <span>&nbsp;
          <span className="badge text-bg-secondary">{label}</span>
        </span>
      );
    }
    return (<span>{username}{moderator}</span>);
  }

  const get_top_right_chunk = () => {
    let
      flagging_count = "",
      flagging_html = "",
      moderate_html = "",
      url = "";

    if (is_removed)
      return "";

    if (is_authenticated && can_moderate && lstate.removal_count > 0) {
      const fmts = django.ngettext(
        "%s user has flagged this comment as inappropriate.",
        "%s users have flagged this comment as inappropriate.",
        lstate.removal_count
      );
      const text = django.interpolate(fmts, [lstate.removal_count]);
      flagging_count = (
        <span className="badge badge-danger" title={text}>
          {lstate.removal_count}
        </span>
      );
    }

    if (allow_flagging) {
      let inapp_msg = "";
      if (lstate.removal) {
        inapp_msg = django.gettext("I flagged it as inappropriate");
        flagging_html = (
          <span>
            {flagging_count}&nbsp;
            <i className="bi bi-flag text-danger" title={inapp_msg}></i>
          </span>
        );
      } else {
        url = (is_authenticated)
          ? flag_url.replace('0', id)
          : login_url + "?next=" + flag_url.replace('0', id);
        inapp_msg = django.gettext("flag comment as inappropriate");
        flagging_html = (
          <a className="mutedlink" href={url}>
            <i className="bi bi-flag" title={inapp_msg}></i>
          </a>
        );
      }
    }

    if (is_authenticated && can_moderate) {
      const remove_msg = django.gettext("remove comment");
      url = delete_url.replace('0', id);
      moderate_html = (
        <a className="mutedlink" href={url}>
          <i className="bi bi-trash" title={remove_msg}></i>
        </a>
      );
    }

    return (<div className="d-inline">{flagging_html} {moderate_html}</div>);
  }

  const get_feedback_chunk = (dir) => {
    if (!allow_feedback)
      return "";

    const attr_list = dir + "_users";  // Produce (dis)like_users
    let show_users_chunk = "";
    let active_user = false;

    if(show_feedback) {
      /* Check whether the user is no longer liking/disliking the
       * comment, and be sure the list of users who liked/disliked
       * the comment is up-to-date.
       */
      const current_user_id = lstate.current_user.split(":")[0];
      const new_user_list = [...lstate[attr_list]];
      let user_ids = new_user_list.map(function(item) {
        return item.split(":")[0];
      });
      active_user = (user_ids.includes(current_user_id)) ? true : false;

      if( // If user expressed opinion, and user not included.
        lstate[dir] && (!user_ids.includes(current_user_id))
      ) { // Then append user.
        new_user_list.push(lstate.current_user);
      } else if( // User has no opinion, and user is included.
        !lstate[dir] && (user_ids.includes(current_user_id))
      ) { // Then remove user.
        new_user_list.splice(user_ids.indexOf(current_user_id), 1);
      }
      // setLstate({...lstate, [attr_list]: new_user_list});

      if(new_user_list.length > 0) {
        let users = new_user_list.map(function(item) {
          return item.split(":")[1];
        });
        users = users.join("<br/>");
        show_users_chunk = (
          <span>&nbsp;
            <a
              className="small" data-bs-html="true"
              data-bs-toggle="tooltip" data-bs-title={users}
            >{new_user_list.length}</a>
          </span>
        );
      }
    }

    const css_class = lstate[dir] ? '' : 'mutedlink';
    let icon = dir == 'like' ? 'hand-thumbs-up' : 'hand-thumbs-down';
    icon += active_user ? '-fill' : '';
    const class_icon = "bi bi-"+icon;
    const click_hdl = dir == 'like' ? action_like : action_dislike;
    const opinion = (dir == 'like')
      ? django.gettext('I like it')
      : django.gettext('I dislike it');

    return (
      <span>
        {show_users_chunk}&nbsp;
        <a
          href="#" onClick={click_hdl} className={css_class}
        ><i className={class_icon} title={opinion}></i></a>&nbsp;
      </span>
    );
  }

  const render_feedback_btns = () => {
    if (!allow_feedback)
      return;

    const feedback_id = "feedback-" + data.id;
    const like_feedback = get_feedback_chunk("like");
    const dislike_feedback = get_feedback_chunk("dislike");

    return (
      <div id={feedback_id} className="d-inline small">{like_feedback}
        <span className="text-muted">&sdot;</span>{dislike_feedback}</div>
    );
  };

  const make_form_invisible = (submit_status) => {
    onCommentCreated();
  }

  const handle_reply_click = (event) => {
    event.preventDefault();

    if (who_can_post === 'users' && !is_authenticated) {
      return window.location.href = (
        `${login_url}?next=${reply_url.replace('0', data.id)}`
      );
    }

    let component = lstate.reply_form.component;
    if (component == undefined) {
      component = (
        <CommentForm
          replyTo={data.id}
          onCommentCreated={make_form_invisible}
        />
      );
    }

    setLstate({
      ...lstate,
      reply_form: {
        component,
        is_visible: !lstate.reply_form.is_visible
      }
    });
  }

  const get_reply_link_chunk = () => {
    if (level >= max_thread_level)
      return;

    let url = reply_url.replace('0', data.id);
    let reply_label = django.gettext("Reply");

    return (allow_feedback)
      ? (
        <span>&nbsp;&nbsp;<span className="text-muted">&bull;</span>&nbsp;&nbsp;
          <a
            className="small mutedlink" href={url} onClick={handle_reply_click}
          >{reply_label}</a>
        </span>
      ) : (
        <a
          className="small mutedlink" href={url} onClick={handle_reply_click}
        >{reply_label}</a>
      );
  }

  const raw_markup = () => {
    var md = new Remarkable();
    const rawMarkup = md.render(comment);
    return { __html: rawMarkup };
  }

  const render_comment_body = () => {
    const extra_space = (allow_feedback) ? "py-1" : "pt-1 pb-3";
    if(is_removed) {
      const cls = `text-muted ${extra_space}`;
      return (<p className={cls}><em>{comment}</em></p>);
    } else {
      const cls = `content ${extra_space}`;
      return (
        <div className={cls} dangerouslySetInnerHTML={raw_markup()}/>
      );
    }
  }

  const render_reply_form = () => {
    if(!lstate.reply_form.is_visible)
      return "";
    return (<div>{lstate.reply_form.component}</div>);
  }

  const post_feedback = (flag) => {
    const _promise = fetch(
      feedback_url,
      {
        method: 'POST',
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ comment: data.id, flag: flag }),
      }
    );
    _promise.then(response => {
      switch (response.status) {
        case 201: {
          if (flag == 'like') {
            const _like_users = [...lstate.like_users, current_user];
            setLstate({
              ...lstate,
              like: true,
              like_users: _like_users,
              dislike: false,
            });
          } else if (flag == 'dislike') {
            const _dislike_users = [...lstate.dislike_users, current_user];
            setLstate({
              ...lstate,
              like: false,
              dislike: true,
              dislike_users: _dislike_users,
            });
          }
        }
        case 204: {
          if (flag == 'like') {
            const user_idx = lstate.like_users.indexOf(current_user);
            const new_like_users = [...lstate.like_users];
            new_like_users.splice(user_idx, 1);
            setLstate({
              ...lstate,
              like: false,
              like_users: new_like_users
            });
          } else if (flag == 'dislike') {
            const user_idx = lstate.like_users.indexOf(current_user);
            const _dislike_users = [...lstate.dislike_users];
            _dislike_users.splice(user_idx, 1);
            setLstate({
              ...lstate,
              dislike: false,
              dislike_users: _dislike_users
            });
          }
        }
        case 400: {
          response.json().then(data => {
            console.error(data);
          });
        }
      }
    });
  }

  const action_like = (event) => {
    event.preventDefault();
    if (is_authenticated) {
      return post_feedback('like');
    }

    const redirect = `${login_url}?next=${like_url.replace('0', id)}`;
    return window.location.href = redirect;
  }

  const action_dislike = (event) => {
    event.preventDefault();
    if (is_authenticated) {
      return post_feedback('dislike');
    }

    const redirect = `${login_url}?next=${dislike_url.replace('0', id)}`;
    return window.location.href = redirect;
  }

  useEffect(() => {
    const qs_tooltip = '[data-bs-toggle="tooltip"]';
    const tooltipTriggerList = document.querySelectorAll(qs_tooltip);
    [...tooltipTriggerList].map(
      tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl)
    );
  }, [lstate]);

  return (
    <div id={`c${data.id}`} className="comment d-flex">
      <img src={user_avatar} className="me-3" height="48" width="48" />
      <div className="d-flex flex-column flex-grow-1 pb-3">
        <h6
          className="comment-header mb-1 d-flex justify-content-between"
          style={{ fontSize: "0.8rem"}}
        >
          <div className="d-inline flex-grow-1">
            {newcids.includes(id) && (
              <span>
                <span className="badge text-bg-success">new</span>&nbsp;-&nbsp;
              </span>
            )}
            {submit_date}&nbsp;-&nbsp;
            {get_username_chunk()}&nbsp;&nbsp;
            <a
              className="permalink text-decoration-none"
              title={django.gettext("comment permalink")}
              href={permalink}
            >¶</a>
          </div>
          {get_top_right_chunk()}
        </h6>
        {render_comment_body()}
        {!is_removed && (
          <div>
            {render_feedback_btns()}
            {get_reply_link_chunk()}
            {render_reply_form()}
          </div>
        )}
        {(children.length > 0) && (
          <div className="pt-3">
            {children?.map((item) => (
              <Comment
                key={item.id}
                data={item}
                onCommentCreated={onCommentCreated}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
