import BaseForm from "./base.js";


const confirm_email_msg = gettext("A confirmation request has been sent to your new email address.");
const make_changes_msg = gettext("The email address did not change.");


export default class EmailForm extends BaseForm {
  constructor(url, formId, formMsgId) {
    super(url, formId, formMsgId);
    this.initial = {
      csrfmiddlewaretoken: this.form.elements['csrfmiddlewaretoken'].value,
      email: this.form.elements['email'].value
    }
  }

  post(_) {
    this.cleanMessage();
    let fields = {
      csrfmiddlewaretoken: this.form.elements['csrfmiddlewaretoken'].value,
      email: this.form.elements['email'].value
    }
    // If email didn't change since the page was loaded there is no
    // need to submit the form. Just inform the user about the fact.
    if (fields['email'] === this.initial['email']) {
      this.setMessage(make_changes_msg, "hide", "alert-info text-info");
      return false;
    }

    let formBody = [];
    for (const field in fields) {
      let key = encodeURIComponent(field);
      let value = encodeURIComponent(fields[field]);
      formBody.push(`${key}=${value}`);
    }
    formBody = formBody.join("&");
    fetch(this.url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset-UTF-8',
      },
      body: formBody
    }).then(response => {
      if (response.status == 200) {
        return response.json();
      }
    }).then(data => {
      if (data.status == "success") {
        this.initial = { ...fields };
        this.setMessage(confirm_email_msg, "hide",
                        "alert-success text-success");
      } else if (data.status == "error") {
        this.setMessage(data.errors.email[0], "hide",
                        "alert-error text-error");
      }
    });
    return false;  // To prevent calling the action attribute.
  }
}
