import BaseForm from "./base.js";


const make_changes_msg = gettext("Your personal profile data did not change.");
const data_saved_msg = gettext("Your personal data has been saved.")

export default class PersonalDataForm extends BaseForm {
  constructor(url, formId, formMsgId) {
    super(url, formId, formMsgId);
    this.name = document.getElementById("user_name");
    this.initial = {
      csrfmiddlewaretoken: this.form.elements['csrfmiddlewaretoken'].value,
      name: this.form.elements['name'].value,
      url: this.form.elements['url'].value
    }
  }

  post(_) {
    this.cleanMessage();
    let fields = {
      csrfmiddlewaretoken: this.form.elements['csrfmiddlewaretoken'].value,
      name: this.form.elements['name'].value,
      url: this.form.elements['url'].value
    }
    // If email didn't change since the page was loaded there is no
    // need to submit the form. Just inform the user about the fact.
    if (
      fields['name'] === this.initial['name'] &&
      fields['url'] === this.initial['url']
    ) {
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
        this.setMessage(data_saved_msg, "hide", "alert-success text-success");
        if (fields['name'].length) {
          this.name.classList.remove("text-muted");
          this.name.textContent = fields['name'];
        }
      } else if (data.status == "error") {
        this.setMessage(data.errors[0], "hide", "alert-error text-error");
      }
    });
    return false;  // To prevent calling the action attribute.
  }
}
