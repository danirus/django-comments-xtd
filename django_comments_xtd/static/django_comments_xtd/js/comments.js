import CommentForm from "./comment_form.js";
import ReplyFormsHandler from "./reply_forms_handler.js";

let comment_form = null;
let reply_forms_handler = null;

function init() {
  if (window.comments_api_props == null)
    return;

  /* ----------------------------------------------
   * Initialize main comment form.
   */
  const qs_cform = "[data-dcx=comment-form]";
  const qs_cform_errors = "[data-dcx=comment-form-errors]";
  if (document.querySelector(qs_cform) &&
      document.querySelector(qs_cform_errors)
  ) {
    comment_form = new CommentForm(qs_cform, qs_cform_errors);
  }

  /* ----------------------------------------------
   * Initialize reply forms.
   */
  const qs_rform = "[data-dcx=reply-form]";
  if (comment_form != null && document.querySelectorAll(qs_rform)) {
    reply_forms_handler = new ReplyFormsHandler(qs_cform, qs_rform);
  }

  window.post_comment_form = (submit_button_name) => (
    comment_form ? comment_form.post(submit_button_name) : false
  );
}

window.addEventListener("DOMContentLoaded", (_) => init());

export default init;
