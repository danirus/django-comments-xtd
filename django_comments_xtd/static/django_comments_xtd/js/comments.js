import CommentForm from "./comment_form.js";
import ReplyFormsHandler from "./reply_forms.js";


function init_comments() {
    if (window.dcx === null) {
        return;
    }

    if (window.dcx.page_param === undefined) {
        const rroot = document.querySelector("[data-dcx=config]");
        if (rroot) {
            window.dcx.page_param = rroot.getAttribute("data-page-qs-param");
        }
    }

    window.dcx.comment_form = null;
    window.dcx.reply_forms_handler = null;

    /* ----------------------------------------------
     * Initialize main comment form.
     */
    const qs_cform = "[data-dcx=comment-form]";
    if (window.dcx.comment_form === null &&
        document.querySelector(qs_cform)
    ) {
        window.dcx.comment_form = new CommentForm(qs_cform);
    }

    /* ----------------------------------------------
     * Initialize reply forms.
     */
    const qs_rform_base = "[data-dcx=reply-form-template]";
    const qs_rforms = "[data-dcx=reply-form]";
    if (window.dcx.reply_forms_handler === null &&
        document.querySelector(qs_rform_base) &&
        document.querySelectorAll(qs_rforms)
    ) {
        window.dcx.reply_forms_handler = new ReplyFormsHandler(qs_rform_base, qs_rforms);
    }
}

export { init_comments };
