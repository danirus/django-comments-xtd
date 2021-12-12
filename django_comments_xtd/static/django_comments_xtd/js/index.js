import CommentForm from "./comment_form.js";
import ReplyFormsHandler from "./reply_forms_handler.js";


let comment_form = null;
let reply_forms_handler = null;

window.addEventListener("DOMContentLoaded", (_) => {
  if (window.comments_api_props != undefined) {
    const qs_cform = "[data-dcx=comment-form]";
    const qs_cform_errors = "[data-dcx=comment-form-errors]";
    if (document.querySelector(qs_cform)) {
      comment_form = new CommentForm(qs_cform, qs_cform_errors);
    }
    reply_forms_handler = new ReplyFormsHandler(
      "comment-form",  // The main comment form in the page.
      "reply-form"  // The class wrapping the form in reply_button.html tmpl.
    );
  }
});

window.post_comment_form = (submit_button_name) => (
  comment_form ? comment_form.post(submit_button_name) : false
);
