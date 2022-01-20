import CommentForm from "./comment_form.js";
import ReplyFormsHandler from "./reply_forms.js";
// import ReplyFormsHandler from "./reply_forms_handler.js";

let comment_form = null;
let reply_forms_handler = null;

function init() {
  if (window.comments_api_props == null)
    return;

  /* ----------------------------------------------
   * Initialize main comment form.
   */
  const qs_cform = "[data-dcx=comment-form]";
  if (document.querySelector(qs_cform)) {
    comment_form = new CommentForm(qs_cform);
  }

  window.post_comment_form = (submit_button_name) => (
    comment_form ? comment_form.post(submit_button_name) : false
  );

  /* ----------------------------------------------
   * Initialize reply forms.
   */
  const qs_rform_base = "[data-dcx=reply-form-template]";
  const qs_rforms = "[data-dcx=reply-form]";
  if (document.querySelector(qs_rform_base) &&
      document.querySelectorAll(qs_rforms)
  ) {
    reply_forms_handler = new ReplyFormsHandler(qs_rform_base, qs_rforms);
  }
}

window.addEventListener("DOMContentLoaded", (_) => init());

export default init;
