import CommentForm from "./comment_form.js";


let comment_form = null;

window.addEventListener("DOMContentLoaded", (_) => {
  if (window.comments_api_props != undefined) {
    if (document.getElementById("comment-form")) {
      comment_form = new CommentForm(
        window.comments_api_props.send_url,
        "comment-form",
        "comment-form-errors"
      );
    }
  }
});

window.post_comment_form = () => comment_form ? comment_form.post() : false;
window.preview_comment = () => comment_form ? comment_form.preview() : false;
