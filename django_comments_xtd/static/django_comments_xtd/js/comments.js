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
  if (document.querySelector(qs_cform)) {
    comment_form = new CommentForm(qs_cform);
  }

  window.post_comment_form = (submit_button_name) => (
    comment_form ? comment_form.post(submit_button_name) : false
  );

  /* ----------------------------------------------
   * Initialize reply forms.
   */
  const base_rform_id = "reply-form";
  const qs_rforms = "[data-dcx=reply-form]";
  if (document.getElementById(base_rform_id) &&
      document.querySelectorAll(qs_rforms)
  ) {
    reply_forms_handler = new ReplyFormsHandler(base_rform_id, qs_rforms);
  }

  window.post_comment_reply_form = (submit_button_name) => (
    reply_forms_handler ? reply_forms_handler.post(submit_button_name) : false
  );
}

window.addEventListener("DOMContentLoaded", (_) => init());

export default init;
