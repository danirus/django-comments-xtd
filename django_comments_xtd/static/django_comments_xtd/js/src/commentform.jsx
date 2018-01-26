import $ from 'jquery';
import django from 'django';

import md5 from 'md5';
import React from 'react';
import ReactDOM from 'react-dom';
import Remarkable from 'remarkable';

import * as lib from './lib.js';


export class CommentForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: '', email: '', url: '', followup: false, comment: '',
      reply_to: this.props.reply_to || 0,
      visited: {name: false, email: false, comment: false},
      errors: {name: false, email: false, comment: false},
      previewing: false,
      alert: {message: '', cssc: ''}
    };
    this.handle_input_change = this.handle_input_change.bind(this);
    this.handle_blur = this.handle_blur.bind(this);
    this.handle_submit = this.handle_submit.bind(this);
    this.handle_preview = this.handle_preview.bind(this);
    this.reset_form = this.reset_form.bind(this);
    this.fhelp = <span className="help-block">{django.gettext("This field is required.")}</span>;
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
    let cssc = "form-group ", help = "";
    if (this.state.errors.comment) {
      cssc += (this.state.errors.comment ? "has-error" : "");
      help = this.fhelp;
    }
    var placeholder = django.gettext("Your comment");
    return (
      <div className={cssc}>
        <div className="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
          <textarea required name="comment" id="id_comment"
                    placeholder={placeholder} maxLength="3000"
                    className="form-control" value={this.state.comment}
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
    let div_cssc = "form-group", input_cssc = "form-control", help = "";
    if (this.state.reply_to > 0) {
      div_cssc += " form-group-sm";
      input_cssc += " input-sm";
    }
    if (this.state.errors.name) {
      div_cssc += " has-error";
      help = this.fhelp;
    }
    var placeholder = django.gettext('name');
    return (
      <div className={div_cssc}>
        <label htmlFor="id_name" className="control-label col-lg-3 col-md-3">
          {django.gettext("Name")}
        </label>
        <div className="col-lg-7 col-md-7">
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
    let div_cssc = "form-group", input_cssc = "form-control";
    if (this.state.reply_to > 0) {
      div_cssc += " form-group-sm";
      input_cssc += " input-sm";
    }
    if (this.state.errors.email)
      div_cssc += " has-error";
    var placeholder = django.gettext('mail address');
    var helptext = django.gettext('Required for comment verification.');
    return (
      <div className={div_cssc}>
        <label htmlFor="id_email" className="control-label col-lg-3 col-md-3">
          {django.gettext("Mail")}
        </label>
        <div className="col-lg-7 col-md-7">
          <input type="text" name="email" required id="id_email"
                 value={this.state.email} placeholder={placeholder}
                 onChange={this.handle_input_change}
                 onBlur={this.handle_blur('email')}
                 className={input_cssc} />
          <span className="help-block">{helptext}</span>
        </div>
      </div>
    );
  }

  render_field_url() {
    if(this.props.is_authenticated)
      return "";
    let div_cssc = "form-group", input_cssc = "form-control";
    if(this.state.reply_to > 0) {
      div_cssc += " form-group-sm";
      input_cssc += " input-sm";
    }
    if(this.state.errors.url)
      div_cssc += " form-group";
    var placeholder = django.gettext("url your name links to (optional)");
    return (
      <div className={div_cssc}>
        <label htmlFor="id_url" className="control-label col-lg-3 col-md-3">
          {django.gettext("Link")}
        </label>
        <div className="col-lg-7 col-md-7">
          <input type="text" name="url" id="id_url" value={this.state.url}
                 placeholder={placeholder}
                 onChange={this.handle_input_change}
                 className={input_cssc} />
        </div>
      </div>
    );
  }

  render_field_followup() {
    let div_cssc = "checkbox";
    if(this.state.reply_to > 0)
      div_cssc += " small";
    var label = django.gettext("Notify me about follow-up comments");
    return (
      <div className="form-group">
        <div className="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
          <div className={div_cssc}>
            <label htmlFor="id_followup">
              <input type="checkbox" checked={this.state.followup}
                     onChange={this.handle_input_change}
                     name="followup" id="id_followup" />
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
    let css_class = "",
	msg_202 = django.gettext("Your comment will be reviewed. Thank your for your patience."),
	msg_204 = django.gettext("Thank you, a comment confirmation request has been sent by mail."),
	msg_403 = django.gettext("Sorry, your comment has been rejected.");

    const message = {202: msg_202,
		     204: msg_204,
		     403: msg_403},
	  cssc = "alert alert-";

    if(status == 403)
      css_class = cssc + "danger";
    else css_class = cssc + "info";

    this.setState({alert: {message: message[status], cssc: css_class},
                   previewing: false});
    this.reset_form();
    this.props.on_comment_created();
  }
  
  handle_submit(event) {
    event.preventDefault();
    if(!this.validate())
      return;

    const data = {
      content_type: this.props.form.content_type,
      object_pk: this.props.form.object_pk,
      timestamp: this.props.form.timestamp,
      security_hash: this.props.form.security_hash,
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
      error: function(xhr, status, err) {
	if(xhr.status == 400) {
	  let errors = this.state.errors;
	  xhr.responseJSON.forEach(function(item, idx, array) {
	    errors[item] = true;
	  });
	  this.setState({errors: errors});
	} else if (xhr.status == 403) {
	  this.handle_submit_response(xhr.status);
	} else {
          console.error(this.props.send_url, status, err.toString());
	}
      }.bind(this)
    });
  }
  
  handle_preview(event) {
    event.preventDefault();
    if(this.validate())
      this.setState({previewing: true});
  }

  rawMarkup() {
    var md = new Remarkable();
    const rawMarkup = md.render(this.state.comment);
    return { __html: rawMarkup };
  }
  
  render_preview() {
    if(!this.state.previewing)
      return "";
    var media_left = "", heading_name = "";

    // Build Gravatar.
    const hash = md5(this.state.email.toLowerCase());
    const avatar_url = "http://www.gravatar.com/avatar/"+hash+"?s=48&d=mm";
    const avatar_img = <img src={avatar_url} height="48" width="48"/>;
    
    if(this.state.url) {
      media_left = <a href={this.state.url}>{avatar_img}</a>;
      heading_name = (<a href={this.state.url} target="_new">
                      {this.state.name}</a>);
    } else {
      media_left = avatar_img;
      if(this.props.is_authenticated)
        heading_name = this.props.current_user.split(":")[1];
      else heading_name = this.state.name;
    }

    let div_cssc = "", div_style = {}, hr_line = <hr/>;
    let label = "";
    var header_text = django.gettext("Your comment in preview");
    let header = <h5 className="text-center">{header_text}</h5>;
    if(this.state.reply_to > 0) {
      div_cssc = "well well-sm";
      div_style = {marginTop: "1em"};
      header = "";
      label = <div className="label label-info">preview</div>;
      hr_line = "";
    }
    var nowtext = django.gettext("Now");
    return (
      <div className={div_cssc} style={div_style}>
        {header}
        <div className="media">
          <div className="media-left">{media_left}</div>
          <div className="media-body">
            <h6 className="media-heading">
              {nowtext}&nbsp;-&nbsp;{heading_name}&nbsp;&nbsp;{label}
            </h6>
            <div className="preview"
                 dangerouslySetInnerHTML={this.rawMarkup()} />
          </div>
        </div>
        {hr_line}
      </div>
    );
  }

  render_form() {
    let comment = this.render_field_comment();
    let name = this.render_field_name();
    let mail = this.render_field_email();
    let url = this.render_field_url();
    let followup = this.render_field_followup();
    let btn_submit_class = "btn btn-primary",
        btn_preview_class = "btn btn-default",
        group_style = {};
    if(this.state.reply_to != 0) {
      btn_submit_class += " btn-sm";
      btn_preview_class += " btn-sm";
      group_style = {marginBottom: "0px"};
    }
    var btn_label_preview = django.gettext("preview");
    var btn_label_send = django.gettext("send");
    
    return (
      <form method="POST" onSubmit={this.handle_submit}
            className="form-horizontal">
        <input type="hidden" name="content_type"
               value={this.props.form.content_type}/>
        <input type="hidden" name="object_pk"
               value={this.props.form.object_pk}/>
        <input type="hidden" name="timestamp"
               value={this.props.form.timestamp}/>
        <input type="hidden" name="security_hash"
               value={this.props.form.security_hash}/>
        <input type="hidden" name="reply_to"
               value={this.state.reply_to}/>
        <fieldset>
          <div style={{display:'none'}}>
            <input type="text" name="honeypot" value=""/>
          </div>
          {comment} {name} {mail} {url} {followup}
        </fieldset>
        
        <div className="form-group" style={group_style}>
          <div className="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
            <input type="submit" name="post" value={btn_label_send}
                   className={btn_submit_class} />&nbsp;
            <input type="button" name="preview" value={btn_label_preview}
                   className={btn_preview_class}
                   onClick={this.handle_preview} />
          </div>
        </div>
      </form>
    );
  }
  
  render() {
    let preview = this.render_preview();
    let header = "";
    let div_class = "well well-sm";
    var label = django.gettext("Post your comment");
    if(this.state.reply_to == 0) {
      header = <h4 className="text-center">{label}</h4>;
      div_class = "well well-lg";
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

    return (
      <div className="comment">
        {preview}
        {header}
        {alert_div}
        <div className={div_class}>
          {form}
        </div>
      </div>
      
    );
  }
}
