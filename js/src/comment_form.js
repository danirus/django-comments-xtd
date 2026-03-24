export default class CommentForm {
  constructor(form_wrapper) {
    this.form_wrapper = form_wrapper;  // A string CSS selector.
    this.form_wrapper_el = undefined; // Element matching form_wrapper.
    this.form_el = undefined;  // <FORM> Element inside form_wrapper_el.

    // True when the comment is posted and
    // the form is no longer available.
    this.form_is_gone = false;

    this.init();
  }

  init() {
    this.form_wrapper_el = document.querySelector(this.form_wrapper);
    this.form_el = this.form_wrapper_el.querySelector("form");
    const post_btn = this.form_el.elements.post;
    const preview_btn = this.form_el.elements.preview;
    post_btn.addEventListener("click", (_) => this.post("post"));
    preview_btn.addEventListener("click", (_) => this.post("preview"));

    // Change the type of the buttons, otherwise the form is submitted.
    post_btn.type = "button";
    preview_btn.type = "button";
  }

  disable_btns(bool_value) {
    this.form_el.elements.post.disabled = bool_value;
    this.form_el.elements.preview.disabled = bool_value;
  }

  is_valid() {
    for (const el of this.form_el.querySelectorAll("[required]")) {
      if (!el.reportValidity()) {
        el.focus();
        return false;
      }
    }
    return true;
  }

  async post(submit_button_name) {
    if (!this.is_valid()) {
      return;
    }
    this.disable_btns(true);

    // If the <section data-djcx="preview">...</section> does exist,
    // delete it. If the user clicks again in the "preview" button
    // it will be displayed again.
    const preview = this.form_wrapper_el.querySelector("[data-djcx=preview]");
    if (preview) {
      preview.remove();
    }

    const form_data = new FormData(this.form_el);
    if (submit_button_name !== undefined) {
      form_data.append(submit_button_name, 1);
    }

    const response = await fetch(this.form_el.action, {
      method: 'POST',
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      body: form_data
    });

    await this.handle_response(response);
    if (!this.form_is_gone) {
      this.disable_btns(false);
    }
    return false; // To prevent calling the action attribute.
  }

  async handle_response(response) {
    const data = await response.json();

    if (response.status === 200) {
      this.form_wrapper_el.innerHTML = data.html;
      this.init();
      if (data.field_focus) {
        this.form_el.querySelector(`[name=${data.field_focus}]`).focus();
      }
    }
    else if (
      response.status === 201 ||
      response.status === 202 ||
      response.status === 400
    ) {
      /* This makes the comment form dissapear. From
       * here on the rest of the methods should not work.
       */
      this.form_el.innerHTML = data.html;
      this.form_is_gone = true;  // The form is gone.
    }
    else if (response.status > 400) {
      alert(
        "Something went wrong and your comment could not be " +
        "processed. Please, reload the page and try again."
      );
    }
  }
}
