import django from 'django';
import React, { useContext, useEffect, useMemo } from 'react';

import { InitContext, StateContext } from './context';
import { Comment } from './comment.jsx';
import { CommentForm } from './commentform.jsx';


function CommentCounter({counter}) {
  const text = useMemo(() => {
    const fmts = django.ngettext("%s comment.", "%s comments.", counter);
    return django.interpolate(fmts, [counter]);
  }, [counter]);

  return (counter > 0)
    ? <h5 className="text-center">{text}</h5>
    : <></>;
}


function CommentFormWrapper({replyTo, onCommentCreated}) {
  const {
    allow_comments,
    who_can_post,
    is_authenticated,
    html_id_suffix,
  } = useContext(InitContext);

  if (allow_comments) {
    if (who_can_post === 'all' ||
      (who_can_post === 'users' && is_authenticated)
    ) {
      return (
        <CommentForm replyTo={replyTo} onCommentCreated={onCommentCreated} />
      );
    }

    const _id = `only-users-can-post-${html_id_suffix}`;
    const elem = document.getElementById(_id);

    return (elem)
      ? <div dangerouslySetInnerHTML={{__html: elem.innerHTML}} />
      : (
        <h5 className="mt-4 mb-5 text-center text-info">
          {django.gettext("Only registered users can post comments.")}
        </h5>
      );
  }

  return (
    <h4 className="mt-4 mb-5 text-center text-secondary">
      {django.gettext("Comments are disabled for this article.")}
    </h4>
  );
}


function UpdateAlert({counter, cids, onClick }) {
  const diff = counter - cids.size;

  if (diff > 0) {
    const fmts = django.ngettext(
      "There is %s new comment.", "There are %s new comments.", diff);
    const message = django.interpolate(fmts, [diff]);

    return (
      <div
        className={(`alert alert-info` +
                   ` d-flex justify-content-between align-items-center`)}>
        <p className="mb-0">{message}</p>
        <button
          type="button" className="btn btn-secondary btn-xs"
          onClick={() => onClick()}>update</button>
      </div>
    );
  } else return <></>;
}


export function CommentBox() {
  const { count_url, list_url, polling_interval } = useContext(InitContext);
  const { state, dispatch } = useContext(StateContext);
  const { counter, cids, tree } = state;

  const load_comments = () => {
    const _promise = fetch(list_url);
    _promise.then(response => {
      return response.json();
    }).then(data => {
      dispatch({ type: 'CREATE_TREE', data });
    }).catch(error => console.error(error));
  }

  const load_count = () => {
    const _promise = fetch(count_url);
    _promise.then(response => {
      return response.json();
    }).then(data => {
      dispatch({ type: 'UPDATE_COUNTER', counter: data.count });
    }).catch(error => console.error(error));
  }

  useEffect(() => {
    if (polling_interval > 0) {
      setInterval(load_count, polling_interval);
    }
    load_comments();
  }, [polling_interval]);

  return (
    <div>
      <CommentCounter counter={counter} />
      <CommentFormWrapper replyTo={0} onCommentCreated={load_comments} />
      <UpdateAlert
        counter={counter} cids={cids} onClick={load_comments}
      />
      <div className="comment-tree">
        {tree.map(item => (
          <Comment
            key={item.id} data={item} onCommentCreated={load_comments}
          />
        ))}
      </div>
    </div>
  );
}
