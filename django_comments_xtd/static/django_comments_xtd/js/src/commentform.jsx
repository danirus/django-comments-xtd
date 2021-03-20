import $ from 'jquery';
import django from 'django';

import React from 'react';
import { Remarkable } from 'remarkable';


export class CommentForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: '', email: '', url: '', comment: '',
      followup: props.default_followup,
      reply_to: this.props.reply_to || 0,
      visited: {name: false, email: false, comment: false},
      errors: {name: false, email: false, comment: false},
      previewing: false,
      alert: {message: '', cssc: ''}
    };
    this.handle_input_change = this.handle_input_change.bind(this);
    this.handle_ajax_error = this.handle_ajax_error.bind(this);
    this.handle_blur = this.handle_blur.bind(this);
    this.handle_submit = this.handle_submit.bind(this);
    this.handle_preview = this.handle_preview.bind(this);
    this.reset_form = this.reset_form.bind(this);
    this.fhelp = <span className="form-text small invalid-feedback">
                   {django.gettext("This field is required.")}
                 </span>;
  }

  handle_input_change(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const iname = target.name;

    this.setState({[iname]: value});
  }

  handle_blur(field) {
    function handler(event) {
      var visited = this.state.visited;
      visited[field] = true;
      this.setState({visited: visited});
    };
    return handler.bind(this);
  }

  validate() {
    var errors = this.state.errors;
    errors.name = false;
    errors.email = false;

    if(!this.state.comment.length)
      errors.comment = true;
    else errors.comment = false;
    if(!this.props.is_authenticated || this.props.request_name) {
      if(/^\s*$/.test(this.state.name))
        errors.name = true;
      else errors.name = false;
    }
    if(!this.props.is_authenticated || this.props.request_email_address) {
      if(/\S+@\S+\.\S+/.test(this.state.email))
        errors.email = false;
      else errors.email = true;
    }
    this.setState({errors: errors});

    if(this.state.errors.comment ||
       this.state.errors.name ||
       this.state.errors.email)
      return false;
    else return true;
  }

  render_field_comment() {
    let div_cssc = "form-group row",
        input_cssc = "form-control",
        help = "";
    if (this.state.reply_to > 0) {
      input_cssc += " form-control-sm";
    }
    if (this.state.errors.comment) {
      div_cssc += (this.state.errors.comment ? " has-danger" : "");
      input_cssc += " is-invalid";
      help = this.fhelp;
    }
    var placeholder = django.gettext("Your comment");
    return (
      <div className={div_cssc}>
        <div className="offset-md-1 col-md-10">
          <textarea required name="comment" id="id_comment"
                    placeholder={placeholder} maxLength="3000"
                    className={input_cssc} value={this.state.comment}
                    onChange={this.handle_input_change}
                    onBlur={this.handle_blur('comment')} />
          {help}
        </div>
      </div>
    );
  }

  render_field_name() {
    if(this.props.is_authenticated && !this.props.request_name)
      return "";
    let div_cssc = "form-group row",
        label_cssc = "col-form-label col-md-3 text-right",
        input_cssc = "form-control",
        help = "";
    const placeholder = django.gettext('name');
    if (this.state.reply_to > 0) {
      label_cssc += " form-control-sm";
      input_cssc += " form-control-sm";
    }
    if (this.state.errors.name) {
      div_cssc += " has-danger";
      input_cssc += " is-invalid";
      help = this.fhelp;
    }
    return (
      <div className={div_cssc}>
        <label htmlFor="id_name" className={label_cssc}>
          {django.gettext("Name")}
        </label>
        <div className="col-md-7">
          <input type="text" name="name" required id="id_name"
                 value={this.state.name} placeholder={placeholder}
                 onChange={this.handle_input_change}
                 onBlur={this.handle_blur('name')}
                 className={input_cssc} />
          {help}
        </div>
      </div>
    );
  }

  render_field_email() {
    if(this.props.is_authenticated && !this.props.request_email_address)
      return "";
    let div_cssc = "form-group row",
        label_cssc = "col-form-label col-md-3 text-right",
        input_cssc = "form-control",
        help_cssc = "form-text small",
        helptext_style = {};
    const placeholder = django.gettext('mail address'),
          helptext = django.gettext('Required for comment verification.');
    if (this.state.reply_to > 0) {
      label_cssc += " form-control-sm";
      input_cssc += " form-control-sm";
      helptext_style = {fontSize: "0.710rem"};
    }
    if (this.state.errors.email) {
      div_cssc += " has-danger";
      input_cssc += " is-invalid";
      help_cssc += " invalid-feedback";
    }
    return (
      <div className={div_cssc}>
        <label htmlFor="id_email" className={label_cssc}>
          {django.gettext("Mail")}
        </label>
        <div className="col-md-7">
          <input type="text" name="email" required id="id_email"
                 value={this.state.email} placeholder={placeholder}
                 onChange={this.handle_input_change}
                 onBlur={this.handle_blur('email')}
                 className={input_cssc} />
          <span className={help_cssc}
                style={helptext_style}>{helptext}</span>
        </div>
      </div>
    );
  }

  render_field_url() {
    if(this.props.is_authenticated)
      return "";
    let label_cssc = "col-form-label col-md-3 text-right",
        input_cssc = "form-control";
    if(this.state.reply_to > 0) {
      label_cssc += " form-control-sm";
      input_cssc += " form-control-sm";
    }
    if(this.state.errors.url)
    var placeholder = django.gettext("url your name links to (optional)");
    return (
      <div className="form-group row">
        <label htmlFor="id_url" className={label_cssc}>
          {django.gettext("Link")}
        </label>
        <div className="col-md-7">
          <input type="text" name="url" id="id_url"
                 value={this.state.url}
                 placeholder={placeholder}
                 onChange={this.handle_input_change}
                 className={input_cssc} />
        </div>
      </div>
    );
  }

  render_field_followup() {
    let label = django.gettext("Notify me about follow-up comments"),
        label_cssc = "custom-control-label",
        elem_id = "id_followup";
    if(this.state.reply_to > 0) {
        label_cssc += " small";
        elem_id += `_${this.state.reply_to}`;
    }
    return (
      <div className="form-group row">
        <div className="offset-md-3 col-md-7">
          <div className="custom-control custom-checkbox">
            <input className="custom-control-input" type="checkbox"
                   checked={this.state.followup}
                   onChange={this.handle_input_change}
                   name="followup" id={elem_id} />
            <label className={label_cssc} htmlFor={elem_id}>
              &nbsp;{label}
            </label>
          </div>
        </div>
      </div>
    );
  }

  reset_form() {
    this.setState({
      name: '', email: '', url: '', followup: false, comment: '',
      visited: {name: false, email: false, comment: false},
      errors: {name: false, email: false, comment: false}
    });
  }

  handle_submit_response(status) {
    let css_class = "";
    const
      msg_202 = django.gettext("Your comment will be reviewed. Thank your for your patience."),
	    msg_204 = django.gettext("Thank you, a comment confirmation request has been sent by mail."),
	    msg_403 = django.gettext("Sorry, your comment has been rejected.");

    const message = {
      202: msg_202,
		  204: msg_204,
		  403: msg_403
    };
	  const cssc = "alert alert-";

    if(status == 403)
      css_class = cssc + "danger";
    else css_class = cssc + "info";

    this.setState({alert: {message: message[status], cssc: css_class},
                   previewing: false});
    this.reset_form();
    this.props.on_comment_created();
  }

  handle_ajax_error(xhr, status, err) {
    if(xhr.status == 400) {
      let errors = this.state.errors;
      xhr.responseJSON.forEach(function(item, idx, array) {
        errors[item] = true;
      });
      this.setState({errors: errors});
    } else if (xhr.status == 403) {
      this.handle_submit_response(xhr.status);
    } else {
      console.error(xhr, status, err.toString());
    }
  }

  handle_submit(event) {
    event.preventDefault();
    if(!this.validate())
      return;

    const data = {
      ...this.props.form,
      honeypot: '',
      comment: this.state.comment,
      name: this.state.name,
      email: this.state.email,
      url: this.state.url,
      followup: this.state.followup,
      reply_to: this.state.reply_to
    };

    $.ajax({
      method: 'POST',
      url: this.props.send_url,
      data: data,
      dataType: 'json',
      cache: false,
      success: function(data, textStatus, xhr) {
        if([201, 202, 204].indexOf(xhr.status) > -1) {
	      this.handle_submit_response(xhr.status);
        }
      }.bind(this),
      error: this.handle_ajax_error
    });
  }

  handle_preview(event) {
    event.preventDefault();
    if(!this.validate())
      return;

    $.ajax({
      method: 'POST',
      url: this.props.preview_url,
      data: { email: this.state.email },
      dataType: 'json',
      success: function(data, textStatus, xhr) {
        if (xhr.status === 200)
          this.setState({
            avatar_url: data.url,
            previewing: true
          });
      }.bind(this),
      error: this.handle_ajax_error
    });
  }

  rawMarkup() {
    var md = new Remarkable();
    const rawMarkup = md.render(this.state.comment);
    return { __html: rawMarkup };
  }

  render_preview() {
    if(!this.state.previewing)
      return "";
    let heading_name = "";

    // Build Gravatar.
    const avatar_img = <img className="mr-3" src={this.state.avatar_url}
                            height="48" width="48"/>;

    if(this.state.url) {
      heading_name = (<a href={this.state.url} target="_new">
                      {this.state.name}</a>);
    } else {
      if(this.props.is_authenticated)
        heading_name = this.props.current_user.split(":")[1];
      else heading_name = this.state.name;
    }

    let label = "";
    var header_text = django.gettext("Your comment in preview");
    let header = <h5 className="text-center">{header_text}</h5>;
    if(this.state.reply_to > 0) {
      header = "";
      label = <div className="badge badge-info">preview</div>;
    }
    var nowtext = django.gettext("Now");
    return (
      <div>
        <hr/>
        {header}
        <div className="media">
          {avatar_img}
          <div className="media-body">
            <div className="comment pb-3">
              <h6 className="mb-1 small">
                {nowtext}&nbsp;-&nbsp;{heading_name}&nbsp;&nbsp;{label}
              </h6>
              <div className="preview"
                   dangerouslySetInnerHTML={this.rawMarkup()} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  render_form() {
    let comment = this.render_field_comment();
    let name = this.render_field_name();
    let mail = this.render_field_email();
    let url = this.render_field_url();
    let followup = this.render_field_followup();
    let btns_row_class = "form-group row";
    let btn_submit_class = "btn btn-primary",
        btn_preview_class = "btn btn-secondary";
    if(this.state.reply_to != 0) {
      btns_row_class += " mb-0";
      btn_submit_class += " btn-sm";
      btn_preview_class += " btn-sm";
    }
    var btn_label_preview = django.gettext("preview");
    var btn_label_send = django.gettext("send");

    return (
      <form method="POST" onSubmit={this.handle_submit}>
        <input type="hidden" name="content_type"
               defaultValue={this.props.form.content_type}/>
        <input type="hidden" name="object_pk"
               defaultValue={this.props.form.object_pk}/>
        <input type="hidden" name="timestamp"
               defaultValue={this.props.form.timestamp}/>
        <input type="hidden" name="security_hash"
               defaultValue={this.props.form.security_hash}/>
        <input type="hidden" name="reply_to"
               defaultValue={this.state.reply_to}/>
        <fieldset>
          <div style={{display:'none'}}>
            <input type="text" name="honeypot" defaultValue=""/>
          </div>
          {comment} {name} {mail} {url} {followup}
        </fieldset>

        <div className={btns_row_class}>
          <div className="offset-md-3 col-md-7">
            <button type="submit" name="post"
                    className={btn_submit_class}>{btn_label_send}</button>&nbsp;
            <button name="preview" className={btn_preview_class}
                   onClick={this.handle_preview}>{btn_label_preview}</button>
          </div>
        </div>
      </form>
    );
  }

  render() {
    let preview = this.render_preview();
    let header = "";
    let div_class = "card card-block mt-2";
    var label = django.gettext("Post your comment");
    if(this.state.reply_to == 0) {
      header = <h4 className="card-title text-center pb-3">{label}</h4>;
      div_class = "card card-block mt-4 mb-5";
    }
    let alert_div = "";
    if(this.state.alert.message) {
      alert_div = (
        <div className={this.state.alert.cssc}>
          {this.state.alert.message}
        </div>
      );
    }
    let form = this.render_form();

    return (<div>
              {preview}
              <div className={div_class}>
                <div className="card-body">
                  {header}
                  {alert_div}
                  {form}
                </div>
              </div>
            </div>);
  }
}
