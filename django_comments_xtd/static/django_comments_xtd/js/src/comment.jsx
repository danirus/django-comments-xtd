import django from 'django';
import React, { useContext, useEffect, useMemo, useState } from 'react';
import { Remarkable } from 'remarkable';

import { getCookie } from './lib.js';
import { InitContext, StateContext } from './context.js';
import { CommentForm } from './commentform.jsx';


// --------------------------------------------------------------------
export function UserPart({
  userName, userUrl, isRemoved, userModerator
}) {
  const user = useMemo(() => {
    return (userUrl && !isRemoved)
      ? <a
        href={userUrl}
        className="text-decoration-none"
        title="User's link">{userName}</a>
      : userName;
  }, [userUrl, isRemoved]);

  const moderator = useMemo(() => {
    if (userModerator) {
      const label = django.gettext("moderator");
      return (
        <span>&nbsp;
          <span className="badge text-bg-secondary">{label}</span>
        </span>
      );
    } else
      return <></>;
  }, [userModerator]);

  return (<span>{user}{moderator}</span>);
}

// --------------------------------------------------------------------
// The TopRightPart displays:
//  * The "flag this comment" link, and
//  * The "remove this comment" link.

export function TopRightPart({
  allowFlagging,
  canModerate,
  commentId,
  deleteUrl,
  flagUrl,
  isAuthenticated,
  isRemoved,
  loginUrl,
  userRequestedRemoval,
  removalCount,
}) {
  const flagging_count = useMemo(() => {
    if (isAuthenticated && canModerate && removalCount > 0) {
      const fmts = django.ngettext(
        "%s user has flagged this comment as inappropriate.",
        "%s users have flagged this comment as inappropriate.",
        removalCount
      );
      const text = django.interpolate(fmts, [removalCount]);
      return (
        <span className="small text-danger" title={text}>{removalCount}</span>
      );
    } else {
      return <></>;
    }
  }, [isAuthenticated, canModerate, removalCount]);

  const flagging_html = useMemo(() => {
    if (!allowFlagging)
      return <></>;

    let inapp_msg = "";
    if (userRequestedRemoval) {
      inapp_msg = django.gettext("I flagged it as inappropriate");
      return (
        <>
          {flagging_count}&nbsp;
          <i className="bi bi-flag text-danger" title={inapp_msg}></i>
        </>
      );
    } else {
      const url = (isAuthenticated)
        ? flagUrl.replace('0', commentId)
        : loginUrl + "?next=" + flagUrl.replace('0', commentId);
      inapp_msg = django.gettext("flag comment as inappropriate");
      return (
        <>
          {flagging_count}&nbsp;
          <a className="text-decoration-none" href={url}>
            <i className="bi bi-flag" title={inapp_msg}></i>
          </a>
        </>
      );
    }
  }, [allowFlagging, userRequestedRemoval]);

  const moderate_html = useMemo(() => {
    if (isAuthenticated && canModerate) {
      const remove_msg = django.gettext("remove comment");
      const url = deleteUrl.replace('0', commentId);
      return (
        <a className="text-decoration-none" href={url}>
          <i className="bi bi-trash" title={remove_msg}></i>
        </a>
      );
    } else {
      return <></>;
    }
  }, [isAuthenticated, canModerate]);

  if (isRemoved)
    return <></>;

  return (
    <div className="d-inline">{flagging_html} {moderate_html}</div>
  )
}


// --------------------------------------------------------------------
// The FeedbackPart displays:
//  * The "flag this comment" link, and
//  * The "remove this comment" link.

export function FeedbackPart({
  allowFeedback,
  commentId,
  currentUser,
  onLikeClicked,
  onDislikeClicked,
  showFeedback,
  userLikeList,
  userDislikeList
}) {
  const cur_user_id = currentUser.split(":")[0];

  const get_user_list = (dir) => {
    return (dir === "like")
      ? userLikeList
      : userDislikeList;
  }

  const get_feedback_chunk = (dir) => {
    if (!allowFeedback)
      return <></>;

    const user_list = [...get_user_list(dir)];
    const userids = new Set(user_list.map(item => item.split(":")[0]));
    const usernames = user_list.map(item => item.split(":")[1]);

    const click_hdl = dir == 'like' ? onLikeClicked : onDislikeClicked;
    let icon = (dir == 'like') ? 'hand-thumbs-up' : 'hand-thumbs-down';
    icon += userids.has(cur_user_id) ? '-fill' : '';
    const class_icon = "bi bi-"+icon;
    const title = (dir == 'like')
      ? django.gettext('I like it')
      : django.gettext('I dislike it');


    return (
      <>
        {showFeedback && (user_list.length > 0) && (
          <a
            className="small text-decoration-none"
            data-bs-html="true"
            data-bs-toggle="tooltip"
            data-bs-title={usernames.join("<br/>")}
          >{user_list.length}</a>
        )}
        <a href="#" onClick={click_hdl}>
          <i className={class_icon} title={title}></i>
        </a>
      </>
    );
  }

  const likeFeedback = get_feedback_chunk("like");
  const dislikeFeedback = get_feedback_chunk("dislike");

  return (allowFeedback
    ? (
      <div id={`feedback-${commentId}`} className="d-inline small">
        {likeFeedback}
        &nbsp;<span className="text-muted">&sdot;</span>&nbsp;
        {dislikeFeedback}
      </div>
    )
    : <></>
  );
}


// --------------------------------------------------------------------
// The ReplyFormPart displays:
//  * The "reply" link. (it can be precedeed with a &bull;)
//  * The "reply" form.

export function ReplyFormPart({
  allowFeedback,
  commentId,
  level,
  maxThreadLevel,
  onCommentCreated,
  onReplyClick,
  replyFormVisible,
  replyUrl,
}) {
  const url = replyUrl.replace('0', commentId);
  const label = django.gettext("Reply");

  if (level >= maxThreadLevel)
    return <></>;

  return (
    <>
      {allowFeedback
        ? (
          <span>
            &nbsp;&nbsp;<span className="text-muted">&bull;</span>&nbsp;&nbsp;
            <a
              className="small text-decoration-none"
              onClick={onReplyClick}
              href={url}
            >{label}</a>
          </span>
        )
        : (
          <a
            className="small text-decoration-none"
            onClick={onReplyClick}
            href={url}
          >{label}</a>
        )
      }
      {replyFormVisible
        ? (
          <CommentForm
            replyTo={commentId}
            onCommentCreated={onCommentCreated}
          />
        )
        : <></>
      }
    </>
  );
}

// --------------------------------------------------------------------
// The CommentBodyPart component.

export function CommentBodyPart({ allowFeedback, comment, isRemoved }) {
  const rawMarkup = useMemo(() => {
    const md = new Remarkable();
    const _markup = md.render(comment);
    return { __html: _markup };
  }, [comment]);

  const extra_space = (allowFeedback) ? "py-1" : "pt-1 pb-3";

  if (isRemoved) {
    const cls = `text-muted ${extra_space}`;
    return <p className={cls}><em>{comment}</em></p>;
  } else {
    const cls = `content ${extra_space}`;
    return <div className={cls} dangerouslySetInnerHTML={rawMarkup}/>;
  }
}

// --------------------------------------------------------------------
export function reduce_flags(data, current_user) {
  const result = {
    like: [],
    dislike: [],
    removal: { is_active: false, count: 0 }
  }
  for (const item of data) {
    const user = [item.id, item.user].join(":");
    switch (item.flag) {
      case "like": {
        result.like.push(user);
        break;
      }
      case "dislike": {
        result.dislike.push(user);
        break;
      }
      case "removal": {
        result.removal.count += 1;
        result.removal.is_active = user === current_user ? true : false;
        break;
      }
    }
  }
  return result;
}


export function Comment(props) {
  const { data } = props;
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

  const _flags = reduce_flags(data.flags, current_user);

  const [lstate, setLstate] = useState({
    current_user: current_user,
    removal: _flags.removal.is_active,
    removal_count: _flags.removal.count,
    like_users: _flags.like,
    dislike_users: _flags.dislike,
    is_reply_form_visible: false
  });

  const handle_comment_created = () => {
    props.onCommentCreated();
    if (is_authenticated) {
      setLstate({ ...lstate, is_reply_form_visible: false });
    }
  }

  const handle_reply_click = (event) => {
    event.preventDefault();

    if (who_can_post === 'users' && !is_authenticated) {
      return window.location.href = (
        `${login_url}?next=${reply_url.replace('0', data.id)}`
      );
    }

    setLstate({
      ...lstate,
      is_reply_form_visible: !lstate.is_reply_form_visible
    });
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
      const _like_users = new Set(lstate.like_users);
      const _dislike_users = new Set(lstate.dislike_users);
      switch (response.status) {
        case 201: {
          if (flag == 'like') {
            _like_users.add(current_user);
            _dislike_users.delete(current_user);
          } else if (flag == 'dislike') {
            _like_users.delete(current_user);
            _dislike_users.add(current_user);
          }
          setLstate({
            ...lstate,
            like_users: [..._like_users],
            dislike_users: [..._dislike_users]
          });
          break;
        }
        case 204: {
          if (flag == 'like') {
            _like_users.delete(current_user);
          } else if (flag == 'dislike') {
            _dislike_users.delete(current_user);
          }
          setLstate({
            ...lstate,
            like_users: [..._like_users],
            dislike_users: [..._dislike_users]
          });
          break;
        }
        case 400: {
          response.json().then(data => {
            console.error(data);
          });
          break;
        }
      }
    });
  }

  const action_like = (event) => {
    event.preventDefault();
    if (is_authenticated) {
      return post_feedback('like');

    }
    const redirect = `${login_url}?next=${like_url.replace('0', data.id)}`;
    return window.location.href = redirect;
  }

  const action_dislike = (event) => {
    event.preventDefault();
    if (is_authenticated) {
      return post_feedback('dislike');
    }

    const redirect = `${login_url}?next=${dislike_url.replace('0', data.id)}`;
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
      <img src={data.user_avatar} className="me-3" height="48" width="48" />
      <div className="d-flex flex-column flex-grow-1 pb-3">
        <h6
          className="comment-header mb-1 d-flex justify-content-between"
          style={{ fontSize: "0.8rem"}}
        >
          <div className="d-inline flex-grow-1">
            {newcids.has(data.id) && (
              <span>
                <span className="badge text-bg-success">new</span>&nbsp;-&nbsp;
              </span>
            )}
            {data.submit_date}&nbsp;-&nbsp;
            <UserPart
              userName={data.user_name}
              userUrl={data.user_url}
              isRemoved={data.is_removed}
              userModerator={data.user_moderator}
            />
            &nbsp;&nbsp;
            <a
              className="permalink text-decoration-none"
              title={django.gettext("comment permalink")}
              href={data.permalink}
            >¶</a>
          </div>
          <TopRightPart
            allowFlagging={allow_flagging}
            canModerate={can_moderate}
            commentId={data.id}
            deleteUrl={delete_url}
            flagUrl={flag_url}
            isAuthenticated={is_authenticated}
            isRemoved={data.is_removed}
            loginUrl={login_url}
            userRequestedRemoval={lstate.removal}
            removalCount={lstate.removal_count}
          />
        </h6>
        <CommentBodyPart
          allowFeedback={allow_feedback}
          comment={data.comment}
          isRemoved={data.is_removed}
        />
        {!data.is_removed && (
          <div>
            <FeedbackPart
              allowFeedback={allow_feedback}
              commentId={data.id}
              currentUser={current_user}
              onLikeClicked={action_like}
              onDislikeClicked={action_dislike}
              showFeedback={show_feedback}
              userLikeList={lstate.like_users}
              userDislikeList={lstate.dislike_users}
            />
            <ReplyFormPart
              allowFeedback={allow_feedback}
              commentId={data.id}
              level={data.level}
              maxThreadLevel={max_thread_level}
              onCommentCreated={handle_comment_created}
              onReplyClick={handle_reply_click}
              replyFormVisible={lstate.is_reply_form_visible}
              replyUrl={reply_url}
            />
          </div>
        )}
        {(data.children.length > 0) && (
          <div className="pt-3">
            {data.children?.map((item) => (
              <Comment
                key={item.id}
                data={item}
                onCommentCreated={props.onCommentCreated}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
