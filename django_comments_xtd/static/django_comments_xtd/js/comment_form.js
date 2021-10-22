export default class CommentForm {
  constructor(url, formElId, errorsElId) {
    this.url = url;
    this.formEl = document.getElementById(formElId);
    this.formEl.action = "";
    this.errorsEl = document.getElementById(errorsElId);
    console.log(`this.initial: `, this.initial);
    console.log(`this.url: `, this.url);
  }

  cleanErrorsEl() {
    const classes = [
      'alert-success', 'alert-info', 'alert-warn', 'alert-error',
      'text-success', 'text-info', 'text-warn', 'text-error'
    ];
    this.errorsEl.classList.add("hide");
    this.errorsEl.textContent = "";
    for (let classname of classes) {
      this.errorsEl.classList.remove(classname);
    }
  }

  setErrorsElText(text, remove_classes, add_classes) {
    for (let classname of remove_classes.split(" ")) {
      this.errorsEl.classList.remove(classname);
    }
    for (let classname of add_classes.split(" ")) {
      this.errorsEl.classList.add(classname);
    }
    this.errorsEl.textContent = text;
  }

  _disable_btns(value) {
    this.formEl.elements['post'].disabled = value;
    this.formEl.elements['preview'].disabled = value;
  }

  preview() {
    this._disable_btns(true);
    console.log(`Preview the comment:`, this.formEl.elements['comment'].value);
    this._disable_btns(false);
    console.log(`post.disabled? `, this.formEl.elements['post'].disabled);
  }

  post() {
    this._disable_btns(true);
    let formBody = {};
    for (const field of this.formEl.elements) {
      formBody[field.name] = field.value;
    }
    formBody.name = (formBody.name == undefined) ? "" : formBody.name;
    formBody.email = (formBody.email == undefined) ? "" : formBody.email;
    const csrftoken = formBody['csrfmiddlewaretoken'];
    delete formBody['csrfmiddlewaretoken'];
    console.log("formBody:", formBody);
    // fetch(this.url, {
    //   method: 'POST',
    //   headers: {
    //     'Accept': 'application/json',
    //     'Content-Type': 'application/json',
    //     'X-CSRFToken': csrftoken,
    //   },
    //   body: JSON.stringify(formBody)
    // }).then(response => {
    //   return response.json();
    // }).then(data => {
    //   console.log(`got response:`, data);
    // });
    this._disable_btns(false);
    console.log(`post.disabled? `, this.formEl.elements['post'].disabled);
    return false;  // To prevent calling the action attribute.
  }
}
