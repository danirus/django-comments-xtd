export default class CommentForm {
  constructor(formWrapper, errorsWrapper) {
    this.formWrapper = formWrapper;
    this.errorsWrapper = errorsWrapper;
    this.url = "";
    this._init();
  }

  _init() {
    this.formWrapperEl = document.querySelector(this.formWrapper);
    this.formEl = this.formWrapperEl.querySelector("form");
    if (!this.url.length) {
      this.url = this.formEl.action;
      this.formEl.action = "";
    }
    this.errorsEl = this.formWrapperEl.querySelector(this.errorsWrapper);
  }

  clean_errors_el() {
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

  set_errors_el_text(text, remove_classes, add_classes) {
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

  _is_valid() {
    for (const el of this.formEl.querySelectorAll("[required]")) {
      if (!el.reportValidity()) {
        return false;
      }
    }
    return true;
  }

  post(submit_button_name) {
    this.clean_errors_el();
    if (!this._is_valid())
      return;
    this._disable_btns(true);
    const formData = new FormData(this.formEl);
    console.log(`submit_button_name:`, submit_button_name);
    if (submit_button_name != undefined)
      formData.append(submit_button_name, 1);
    console.log("formData:", formData);
    fetch(this.url, {
      method: 'POST',
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      },
      body: formData
    }).then(response => {
      if (submit_button_name == "preview")
        this.handle_preview_comment_response(response);
      else if (submit_button_name == "post")
        this.handle_post_comment_response(response);
    });
    this._disable_btns(false);
    return false;  // To prevent calling the action attribute.
  }

  async handle_preview_comment_response(response) {
    if (response.status == 200 || response.status == 422) {
      content = await response.text();
      this.formWrapperEl.innerHTML = content;
      this._init();
    }
  }

  async handle_post_comment_response(response) {
    debugger;
    if (response.status == 422) {
      content = await response.text();
      console.log(`handle_post_comment_response status:`, response.status);
      console.log(`handle_post_comment_response content:`, content);
      this.formEl.innerHTML = content;
      this._init();
    } else if (response.status >= 400 && response.status < 500) {
      this.set_errors_el_text(
        "Something went wrong, your comment can not be processed.",
        "hide", "alert-error text-error"
      );
    }
  }
}
