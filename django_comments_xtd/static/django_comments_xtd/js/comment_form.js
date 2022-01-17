export default class CommentForm {
  constructor(formWrapper) {
    this.formWrapper = formWrapper;
    this.url = "";  // Form action URL.
    this._init();
  }

  _init() {
    this.formWrapperEl = document.querySelector(this.formWrapper);
    this.formEl = this.formWrapperEl.querySelector("form");
    if (!this.url.length) {
      this.url = this.formEl.action;
      this.formEl.action = "";
    }
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
    // this.clean_errors_el();
    if (!this._is_valid())
      return;
    this._disable_btns(true);

    // If the <section data-dcx="preview">...</section> does exist,
    // delete it. If the user clicks again in the "preview" button
    // it will be displayed again.
    const preview = this.formWrapperEl.querySelector("[data-dcx=preview]");
    if (preview) {
      preview.remove();
    }

    const formData = new FormData(this.formEl);
    if (submit_button_name != undefined)
      formData.append(submit_button_name, 1);

    fetch(this.url, {
      method: 'POST',
      headers: {
        "X-Requested-With": "XMLHttpRequest",
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
    if (response.status == 200 || response.status == 400) {
      const data = await response.json();
      this.formWrapperEl.innerHTML = data.html;
      this._init();
    }
  }

  async handle_post_comment_response(response) {
    if (response.status == 200 || response.status == 400) {
      const data = await response.json();
      this.formEl.innerHTML = data.html;
      this._init();
    } else if (response.status == 201) {
      const data = await response.json();
      location.href = data.html;
    } else if (response.status > 400 && response.status < 500) {
      alert(
        "Something went wrong and your comment could not be processed." +
        "Please, reload the page and try again."
      );
    }
  }
}
