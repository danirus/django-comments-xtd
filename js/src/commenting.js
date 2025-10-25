import CommentForm from "./comment_form";
import CommentThreads from "./comment_threads";
import ReplyFormHandler from "./reply_forms";


function init_commenting(cfg) {
  if (!globalThis.djcx) {
    return;
  }

  // Highlight the visual elements that make up threads of comments.
  globalThis.djcx.cthreads = CommentThreads.initialize();

  globalThis.djcx.comment_form = undefined;
  globalThis.djcx.reply_forms_handler = undefined;

  /* ----------------------------------------------
   * Initialize main comment form.
   */
  const qs_cform = "[data-djcx=comment-form]";
  if (
    globalThis.djcx.comment_form === undefined
    && document.querySelector(qs_cform)
  ) {
    globalThis.djcx.comment_form = new CommentForm(qs_cform);
  }

  /* ----------------------------------------------
   * Initialize reply forms.
   */
  const qs_rform_base = "[data-djcx=reply-form-template]";
  const qs_rforms = "[data-djcx=reply-form]";
  if (
    globalThis.djcx.reply_form_handler === undefined
    && document.querySelector(qs_rform_base)
    && document.querySelectorAll(qs_rforms)
  ) {
    globalThis.djcx.reply_form_handler = new ReplyFormHandler(
      qs_rform_base, qs_rforms
    );
  }
}

export { init_commenting };
