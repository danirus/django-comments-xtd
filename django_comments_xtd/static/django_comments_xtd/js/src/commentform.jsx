import django from 'django';
import React, { useContext, useState } from 'react';
import { Remarkable } from 'remarkable';

import { getCookie } from './lib.js';
import { InitContext } from './context';


export function FieldIsRequired({replyTo}) {
  return (
    <span
      className="form-text small invalid-feedback"
      {...((replyTo > 0) && {style: {"fontSize": "0.71rem"}})}
    >
      {django.gettext("This field is required.")}
    </span>
  );
}


export function PreviewComment({avatar, name, url, comment, replyTo}) {
  const {
    is_authenticated,
    current_user
  } = useContext(InitContext);

  const get_heading_name = () => {
    if (url.length > 0)
      return (<a href={url} target="_new">{name}</a>);
    else if (is_authenticated)
      return current_user.split(":")[1];
    else
      return name;
  }

  const raw_markup = () => {
    const md = new Remarkable();
    const _raw_markup = md.render(comment);
    return { __html: _raw_markup };
  }

  return (
    <div>
      <hr />
      {!replyTo && (
        <h5 className="text-center">
          {django.gettext("Your comment in preview")}
        </h5>
      )}
      <div className={`comment d-flex ` + ((replyTo > 0) ? "mt-1" : "mt-5")}>
        <img className="me-3" src={avatar} height="48" width="48" />
        <div className="d-flex flex-column pb-3">
          <span style={{fontSize: "0.8rem"}}>
            {django.gettext("Now")} - {get_heading_name()}  {replyTo > 0 && (
              <div className="badge badge-info">preview</div>
            )}</span>
          <div
            className="content py-2"
            dangerouslySetInnerHTML={raw_markup()}
          />
        </div>
      </div>
    </div>
  );
}


export function CommentForm({ replyTo, onCommentCreated }) {
  const {
    default_followup,
    default_form,
    is_authenticated,
    preview_url,
    request_email_address,
    request_name,
    send_url
  } = useContext(InitContext);

  const [lstate, setLstate] = useState({
    previewing: false,
    submitted: false,
    avatar: undefined, name: "", email: "", url: "", comment: "",
    followup: default_followup,
    errors: { name: false, email: false, comment: false },
    alert: { message: "", cssc: "" }
  });

  const handle_input_change = (event) => {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const iname = target.name;

    setLstate({ ...lstate, [iname]: value });
  }

  const is_valid_data = () => {
    let is_valid_name = true, is_valid_email = true;

    if (!is_authenticated || request_name)
      is_valid_name = (/^\s*$/.test(lstate.name)) ? false : true;

    if (!is_authenticated || request_email_address)
      is_valid_email = (/\S+@\S+\.\S+/.test(lstate.email)) ? true : false;

    const is_valid_comment = (/^\s*$/.test(lstate.comment)) ? false : true;

    setLstate({
      ...lstate,
      errors: {
        ...lstate.errors,
        name: !is_valid_name,
        email: !is_valid_email,
        comment: !is_valid_comment
      }
    });

    return is_valid_name && is_valid_email && is_valid_comment;
  }

  const handle_submit = (event) => {
    event.preventDefault();
    if (!is_valid_data()) {
      return;
    }

    const data = {
      ...default_form,
      honeypot: '',
      comment: lstate.comment,
      name: lstate.name,
      email: lstate.email,
      url: lstate.url,
      followup: lstate.followup,
      reply_to: replyTo
    };

    const _promise = fetch(
      send_url,
      {
        method: 'POST',
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(data),
      }
    );
    _promise.then(response => {
      if ([201, 202, 204, 403].includes(response.status)) {
        let css_class = "";
        const msg_202 = django.gettext(
          "Your comment will be reviewed. Thank your for your patience.");
        const msg_204 = django.gettext(
          "Thank you, a comment confirmation request has been sent by mail.");
        const msg_403 = django.gettext(
          "Sorry, your comment has been rejected.");
        const message = {
          202: msg_202,
          204: msg_204,
          403: msg_403
        };


        const cssc = (replyTo > 0 ? "mb-0 " : "") + "small alert alert-";
        css_class = (response.status == 403) ? cssc + "danger" : cssc + "info";

        const _errors = response.status < 300
          ? { name: false, email: false, comment: false }
          : { ...lstate.errors };

        setLstate({
          ...lstate,
          alert: {
            message: message[response.status],
            cssc: css_class
          },
          previewing: false,
          submitted: true,
          name: '', email: '', url: '', followup: false, comment: '',
          errors: _errors
        });

        onCommentCreated();
      }
    })
  }

  const handle_preview = (event) => {
    event.preventDefault();
    if (!is_valid_data())
      return;

    const _promise = fetch(
      preview_url,
      {
        method: 'POST',
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ email: lstate.email }),
      }
    );
    _promise.then(response => {
      if (response.status === 200)
        return response.json();
      else throw new Error(`Status ${response.status}`);
    }).then(data => {
      setLstate({
        ...lstate,
        avatar: data.url,
        previewing: true
      });
    }).catch(error => console.error(error));
  }

  const get_field_css_classes = (field) => {
    let css_classes = "row justify-content-center form-group";
    if (field === "followup")
      css_classes += " my-3";
    else
      css_classes += (replyTo > 0) ? " my-2" : " my-3";

    if (   (field === "name" && lstate.errors.name)
        || (field === "email" && lstate.errors.email)
        || (field === "comment" && lstate.errors.comment)
    ) {
      css_classes += " has-danger";
    }

    return css_classes;
  }

  const get_input_css_classes = (field) => {
    let css_classes = "form-control";
    css_classes += (replyTo > 0) ? " form-control-sm" : "";

    if (   (field === "name" && lstate.errors.name)
        || (field === "email" && lstate.errors.email)
        || (field === "comment" && lstate.errors.comment)
    ) {
      css_classes += " is-invalid";
    }

    return css_classes;
  }

  const render_comment_field = () => {
    return (
      <div className={get_field_css_classes("comment")}>
        <div className={(replyTo > 0) ? "col-12" : "col-10"}>
          <textarea
            required name="comment" id="id_comment"
            value={lstate.comment} maxLength={3000}
            placeholder={django.gettext("Your comment")}
            className={get_input_css_classes("comment")}
            onChange={handle_input_change}
          />
          {lstate.errors.comment && <FieldIsRequired replyTo={replyTo} />}
        </div>
      </div>
    );
  }

  const render_name_field = () => {
    if (is_authenticated && !request_name)
      return <></>;

    return (
      <div className={get_field_css_classes("name")}>
        <div className="col-2 text-end">
          <label
            htmlFor="id_name"
            className={
              (replyTo > 0) ? "form-control-sm" : "col-form-label"
            }
          >{django.gettext("Name")}</label>
        </div>
        <div className={(replyTo > 0) ? "col-9" : "col-7"}>
          <input
            required type="text" name="name" id="id_name"
            value={lstate.name} placeholder={django.gettext('name')}
            onChange={handle_input_change}
            className={get_input_css_classes("name")}
          />
          {lstate.errors.name && <FieldIsRequired replyTo={replyTo} />}
        </div>
      </div>
    );
  }

  const render_email_field = () => {
    if (is_authenticated && !request_email_address)
      return <></>;

    let help_cssc = "form-text small";
    help_cssc += lstate.errors.email ? " invalid-feedback" : "";

    return (
      <div className={get_field_css_classes("email")}>
        <div className="col-2 text-end">
          <label
            htmlFor="id_name"
            className={
              (replyTo > 0) ? "form-control-sm" : "col-form-label"
            }
          >{django.gettext("Mail")}</label>
        </div>
        <div className={(replyTo > 0) ? "col-9" : "col-7"}>
          <input
            required type="text" name="email" id="id_email"
            value={lstate.email} placeholder={django.gettext('mail address')}
            onChange={handle_input_change}
            className={get_input_css_classes("email")}
          />
          <span
            className={help_cssc}
            {...((replyTo > 0) && {style: {"fontSize": "0.71rem"}})}
          >
            {django.gettext('Required for comment verification.')}
          </span>
        </div>
      </div>
    );
  }

  const render_url_field = () => {
    if (is_authenticated)
      return <></>;

    return (
      <div className={get_field_css_classes("url")}>
        <div className="col-2 text-end">
          <label
            htmlFor="id_url"
            className={
              (replyTo > 0) ? "form-control-sm" : "col-form-label"
            }
          >{django.gettext("Link")}</label>
        </div>
        <div className={(replyTo > 0) ? "col-9" : "col-7"}>
          <input
            type="text" name="url" id="id_url"
            value={lstate.url}
            placeholder={django.gettext("url your name links to (optional)")}
            onChange={handle_input_change}
            className={get_input_css_classes("url")}
          />
        </div>
      </div>
    );
  }

  const render_followup_field = () => {
    const elem_id = (replyTo > 0) ? `_${replyTo}` : "id_followup";
    const cssc = "form-check d-flex justify-content-center align-items-center";

    return (
      <div className={get_field_css_classes("followup")}>
        <div className={(replyTo > 0) ? "col-10" : "col-7"}>
          <div className={cssc}>
            <input
              name="followup" type="checkbox"
              id={elem_id}
              onChange={handle_input_change}
              className="form-check-input"
              checked={lstate.followup}
            />
            <label
              htmlFor={elem_id}
              className={"ps-2 form-check-label" + (replyTo > 0 && " small")}
            >
              &nbsp;{django.gettext("Notify me about follow-up comments")}
            </label>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      {lstate.previewing && (
        <PreviewComment
          avatar={lstate.avatar}
          name={lstate.name}
          url={lstate.url}
          comment={lstate.comment}
          replyTo={replyTo}
        />
      )}
      <div className={(replyTo === 0) ? "card mt-4 mb-5" : "card mt-2"}>
        <div className="card-body">
          {(replyTo === 0) && (
            <h4 className="card-title text-center pb-3">
              {django.gettext("Post your comment")}
            </h4>
          )}
          {(lstate.alert.message && lstate.alert.message.length > 0) && (
            <div className={lstate.alert.cssc}>{lstate.alert.message}</div>
          )}
          {(!lstate.submitted || replyTo === 0) && (
            <form method="POST" onSubmit={handle_submit}>
              <fieldset>
                <input type="hidden" name="content_type"
                  defaultValue={default_form.content_type} />
                <input type="hidden" name="object_pk"
                  defaultValue={default_form.object_pk} />
                <input type="hidden" name="timestamp"
                  defaultValue={default_form.timestamp} />
                <input type="hidden" name="security_hash"
                  defaultValue={default_form.security_hash} />
                <input type="hidden" name="reply_to"
                  defaultValue={replyTo} />
                <div style={{display:'none'}}>
                  <input type="text" name="honeypot" defaultValue="" />
                </div>
                {render_comment_field()}
                {render_name_field()}
                {render_email_field()}
                {render_url_field()}
                {render_followup_field()}
              </fieldset>
              <div
                className={
                  "row my-2 form-group" + (replyTo > 0 ? " mb-0" : "")
                }
              >
                <div className="d-flex justify-content-center">
                  <button
                    type="submit"
                    name="post"
                    className={
                      "btn btn-primary me-1" + (replyTo > 0 ? " btn-sm" : "")
                    }
                  >{django.gettext("send")}</button>
                  <button
                    name="preview"
                    className={
                      "btn btn-secondary" + (replyTo > 0 ? " btn-sm" : "")
                    }
                    onClick={handle_preview}
                  >{django.gettext("preview")}</button>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
