export default class ReplyFormHandler {
  constructor(qs_reply_form_base, qs_reply_forms) {
    this.reply_form_base = document.querySelector(qs_reply_form_base);
    this.reply_map = new Map();
    this.opened_id = 0;

    for (const elem of document.querySelectorAll(qs_reply_forms)) {
      // Extract the reply_to value from the current reply_form
      // (provided by the Django template reply_button.html).
      // Then replace the content of elem with a copy of the
      // generic this.replyFormBase and update the field
      // reply_to so that it has the same value given in
      // the original django template.
      const rform_el = elem.querySelector("form");
      if (rform_el === null) {
        console.error(
          `Could not find a reply form within one of ` +
          `the elements retrieved with selector: ${qs_reply_forms}.`
        );
        return;
      }

      const reply_to = Number.parseInt(rform_el.elements.reply_to.value);
      const section = this.reply_form_base.cloneNode(true);
      section.dataset.djcx = `reply-form-${reply_to}`;

      // Update field reply_to.
      const new_form = section.querySelector("form");
      new_form.elements.reply_to.value = reply_to;

      const elem_parent = elem.parentNode;
      elem.replaceWith(section);
      this.init(reply_to);
      this.reply_map.set(reply_to, elem_parent);
    }

    this.on_document_click = this.on_document_click.bind(this);
    this.on_document_key_up = this.on_document_key_up.bind(this);
    globalThis.document.addEventListener('click', this.on_document_click);
    globalThis.document.addEventListener('keyup', this.on_document_key_up);
  }

  init(reply_to, is_active) {
    const qs_section = `[data-djcx=reply-form-${reply_to}]`;
    const section = document.querySelector(qs_section);

    // Modify the form (update fields, add event listeners).
    const new_form = section.querySelector("form");
    const post_btn = new_form.elements.post;
    post_btn.addEventListener("click", this.send_clicked(reply_to));
    const preview_btn = new_form.elements.preview;
    preview_btn.addEventListener("click", this.preview_clicked(reply_to));
    const cancel_btn = new_form.elements.cancel;
    cancel_btn.addEventListener("click", this.cancel_clicked(reply_to));
    new_form.style.display = "none";

    // Attach event listener to textarea.
    const divta = section.querySelector("[data-djcx=reply-textarea]");
    const ta = divta.querySelector("textarea");
    ta.addEventListener("focus", this.textarea_focus(reply_to));

    // If is_active is true, hide the textarea and display the form.
    if (is_active === true) {
      section.classList.add("active");
      divta.style.display = "none";
      new_form.style = "";
      new_form.elements.comment.focus();
    }
  }

  get_map_item(reply_to) {
    const item = this.reply_map.get(reply_to);
    if (item === undefined) {
      const msg = `replyMap doesn't have a key ${reply_to}`;
      console.error(msg);
      throw msg;
    }
    return item;
  }

  disable_buttons(form_el, value) {
    form_el.elements.post.disabled = value;
    form_el.elements.preview.disabled = value;
  }

  is_valid(form_el) {
    for (const elem of form_el.querySelectorAll("[required]")) {
      if (!elem.reportValidity()) {
        elem.focus();
        return false;
      }
    }
    return true;
  }

  on_document_click(event) {
    const reply_section = event.target.closest(`section[data-djcx]`);
    const data_attr = (
      reply_section
      && reply_section.dataset
      && reply_section.dataset.djcx
    ) || undefined;
    if (
      this.opened_id !== 0 && (
        data_attr === undefined || data_attr !== `reply-form-${this.opened_id}`
      )
    ) {
      console.log(
        "ReplyFormHandler.on_document_click called. "
        + `this_opened_id = ${this.opened_id}.`
      );
      this.cancel_clicked(this.opened_id)();
    }
  }

  on_document_key_up(event) {
    if (event.key === "Escape" && this.opened_id !== 0) {
      console.log(
        "ReplyFormHandler.on_document_key_up called. "
        + `this_opened_id = ${this.opened_id}.`
      );
      this.cancel_clicked(this.opened_id)();
    }
  }

  textarea_focus(reply_to) {
    // Display the comment form and hide the text area.
    return (_) => {
      this.opened_id = reply_to;
      const item = this.get_map_item(reply_to);
      const qs_section = `[data-djcx=reply-form-${reply_to}`;
      const section = item.querySelector(qs_section);
      const form = section.querySelector("form");
      const divta = section.querySelector("[data-djcx=reply-textarea]");
      section.classList.toggle("active");
      divta.style.display = "none";
      form.style = "";
      form.elements.comment.focus();
    };
  }

  cancel_clicked(reply_to) {
    // Display the text area and hide the comment form.
    return (_) => {
      const item = this.get_map_item(reply_to);
      const qs_section = `[data-djcx=reply-form-${reply_to}]`;
      const section = item.querySelector(qs_section);
      const form = section.querySelector("form");
      const divta = section.querySelector("[data-djcx=reply-textarea]");
      const comment_value = form.elements.comment.value;
      divta.querySelector("textarea").value = comment_value;
      section.classList.toggle("active");
      form.style.display = "none";
      divta.style = "";

      const preview_elem = item.querySelector("[data-djcx=preview]");
      if (preview_elem) {
        preview_elem.remove();
      }
      this.opened_id = 0;
    };
  }

  preview_clicked(reply_to) {
    return (_) => {
      this.post("preview", reply_to);
    };
  }

  send_clicked(reply_to) {
    return (_) => {
      this.post("post", reply_to);
    };
  }

  post(submit_button_name, reply_to) {
    const item = this.get_map_item(reply_to);
    const form_elem = item.querySelector("form");

    if (!this.is_valid(form_elem)) {
      return;
    }

    this.disable_buttons(form_elem, true);

    const preview_elem = item.querySelector("[data-dci=preview]");
    if (preview_elem) {
      preview_elem.remove();
    }

    const form_data = new FormData(form_elem);
    if (submit_button_name !== undefined) {
      form_data.append(submit_button_name, 1);
    }

    fetch(form_elem.action, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      body: form_data
    }).then(response => {
      if (submit_button_name === "preview") {
        this.handle_preview_comment_response(response, reply_to);
      } else if (submit_button_name === "post") {
        this.handle_post_comment_response(response, reply_to);
      }
    });
    this.disable_buttons(form_elem, false);
    return false; // To prevent calling the action attribute.
  }

  handle_http_200(item, data, reply_to) {
    item.innerHTML = data.html;
    this.init(reply_to, true); // 2nd param: is_active = true.
    if (data.field_focus) {
      item.querySelector(`[name=${data.field_focus}]`).focus();
    }
  }

  handle_http_201_202_400(item, data) {
    const form = item.querySelector("form");
    form.innerHTML = data.html;
  }

  async handle_preview_comment_response(response, reply_to) {
    const item = this.get_map_item(reply_to);
    const data = await response.json();

    if (response.status === 200) {
      this.handle_http_200(item, data, reply_to);
    } else if (response.status === 400) {
      this.handle_http_201_202_400(item, data);
    }
  }

  async handle_post_comment_response(response, reply_to) {
    const item = this.get_map_item(reply_to);
    const data = await response.json();

    if (response.status === 200) {
      this.handle_http_200(item, data, reply_to);
    }
    else if (
      response.status === 201 ||
      response.status === 202 ||
      response.status === 400
    ) {
      this.handle_http_201_202_400(item, data);
    }
    else if (response.status > 400) {
      alert(
        "Something went wrong and your comment could not be " +
        "processed. Please, reload the page and try again."
      );
    }
  }
}