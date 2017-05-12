import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';


export class CommentForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: '', email: '', url: '', followup: false, comment: '',
      visited: {name: false, email: false, comment: false},
      errors: {name: false, email: false, comment: false}
    };
    this.handle_input_change = this.handle_input_change.bind(this);
    this.handle_blur = this.handle_blur.bind(this);
    this.handle_submit = this.handle_submit.bind(this);
    this.handle_preview = this.handle_preview.bind(this);
    this.fhelp = <span className="help-block">This field is required.</span>;
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

    if(!this.state.comment.length)
      errors.comment = true;
    else errors.comment = false;
    if(!this.props.settings.is_authenticated) {
      if(!this.state.name.length)
        errors.name = true;
      else errors.name = false;
      if(/\S+@\S+\.\S+/.test(this.state.email))
        errors.email = false;
      else errors.email = true;
    } else {
      errors.name = false;
      errors.email = false;
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
    return (
      <div className={cssc}>
        <div className="col-lg-offset-1 col-md-offset-1 col-lg-10 col-md-10">
          <textarea required name="comment" id="id_comment"
                    placeholder="Your comment" maxLength="3000"
                    className="form-control" value={this.state.comment}
                    onChange={this.handle_input_change}
                    onBlur={this.handle_blur('comment')} />
          {help}
        </div>
      </div>
    );
  }

  render_field_name() {
    if(this.props.settings.is_authenticated)
      return "";
    let cssc = "form-group ", help = "";
    if (this.state.errors.name) {
      cssc += (this.state.errors.name ? "has-error" : "");
      help = this.fhelp;
    }
    return (
      <div className={cssc}>
        <label htmlFor="id_name" className="control-label col-lg-3 col-md-3">
          Name
        </label>
        <div className="col-lg-7 col-md-7">
          <input type="text" name="name" required id="id_name"
                 value={this.state.name} placeholder="name"
                 onChange={this.handle_input_change}
                 onBlur={this.handle_blur('name')}
                 className="form-control" />
          {help}
        </div>
      </div>
    );
  }

  render_field_email() {
    if(this.props.settings.is_authenticated)
      return "";
    let cssc = "form-group " + (this.state.errors.email ? "has-error" : "");
    return (
      <div className={cssc}>
        <label htmlFor="id_email" className="control-label col-lg-3 col-md-3">
          Mail
        </label>
        <div className="col-lg-7 col-md-7">
          <input type="text" name="email" required id="id_email"
                 value={this.state.email} placeholder="mail address"
                 onChange={this.handle_input_change}
                 onBlur={this.handle_blur('email')}
                 className="form-control" />
          <span className="help-block">Required for comment verification.</span>
        </div>
      </div>
    );
  }

  render_field_url() {
    if(this.props.settings.is_authenticated)
      return "";
    let cssc = "form-group " + (this.state.errors.url ? "has-error" : "");
    return (
      <div className={cssc}>
        <label htmlFor="id_url" className="control-label col-lg-3 col-md-3">
          Link
        </label>
        <div className="col-lg-7 col-md-7">
          <input type="text" name="url" id="id_url" value={this.state.url}
                 placeholder="url your name links to (optional)"
                 onChange={this.handle_input_change}
                 className="form-control" />
        </div>
      </div>
    );
    return "";
  }

  render_field_followup() {
    return (
      <div className="form-group">
        <div className="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
          <div className="checkbox">
            <label htmlFor="id_followup">
              <input type="checkbox" checked={this.state.followup}
                     onChange={this.handle_input_change}
                     name="followup" id="id_followup"/>
              &nbsp;&nbsp;
              Notify me about follow-up comments
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
  
  handle_submit(event) {
    event.preventDefault();
    if(!this.validate())
      return;
    const cssc = "text-center alert alert-";
    const message = {
      202: "Your comment will be reviewed. Thank your for your patience.",
      204: "Thank you, a comment confirmation request has been sent by mail.",
      403: "Sorry, your comment has been rejected."
    };
    $.ajax({
      method: 'POST',
      url: this.props.settings.send_url,
      data: {
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
        reply_to: 0
      },
      dataType: 'json',
      cache: false,
      statusCode: {
        201: function() {
          this.reset_form();
          this.props.reloadComments();
        }.bind(this),
        202: function() {
          this.reset_form();
          this.props.onCommentSubmit({'message': message[202],
                                      'cssc': cssc+"info"});
        }.bind(this),
        204: function() {
          this.reset_form();
          this.props.onCommentSubmit({'message': message[204],
                                      'cssc': cssc+"info"});
        }.bind(this),
        403: function() {
          this.reset_form();
          this.props.onCommentSubmit({'message': message[403],
                                      'cssc': cssc+"danger"});
        }.bind(this)
      },
      error: function(xhr, status, err) {
        console.error(this.props.settings.send_url, status, err.toString());
      }.bind(this)
    });
  }
  
  handle_preview(event) {
    event.preventDefault();
    if(this.validate()) {
      this.props.onCommentPreview(this.state.name,
                                  this.state.email,
                                  this.state.url,
                                  this.state.comment);
    }
  }
  
  render() {
    let comment = this.render_field_comment();
    let name = this.render_field_name();
    let mail = this.render_field_email();
    let url = this.render_field_url();
    let followup = this.render_field_followup();
    
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
        <fieldset>
          <div style={{display:'none'}}>
            <input type="text" name="honeypot" value=""/>
          </div>
          {comment} {name} {mail} {url} {followup}
        </fieldset>

        <div className="form-group">
          <div className="col-lg-offset-3 col-md-offset-3 col-lg-7 col-md-7">
            <input type="submit" name="post" value="send"
                   className="btn btn-primary"/>&nbsp;
            <input type="button" name="preview" value="preview"
                   className="btn btn-default" onClick={this.handle_preview} />
          </div>
        </div>
      </form>
    );
  }
}
