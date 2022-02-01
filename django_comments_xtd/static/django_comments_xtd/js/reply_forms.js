export default class ReplyFormsHandler {
    constructor(qsReplyFormBase, qsReplyForms) {
        this.replyFormBase = document.querySelector(qsReplyFormBase);
        this.replyMap = new Map();

        const cpage_field = window.dcx.page_param || "cpage";

        for (const elem of document.querySelectorAll(qsReplyForms)) {
            // Extract the reply_to value from the current reply_form.
            // Also, it if does exist, extract the comment's page number too.
            // Then replace the content of elem with a copy of
            // this.replyFormBase and update the fields reply_to
            // and comment's page number.
            const rFormEl = elem.querySelector("form");
            if (rFormEl === null) {
                console.error(
                    `Could not find a reply form within one of ` +
                    `the elements retrieved with ${qsReplyForms}.`
                );
                return;
            }

            const reply_to = rFormEl.elements.reply_to.value;
            const cpage = rFormEl.elements[cpage_field]
                ? rFormEl.elements[cpage_field].value
                : null;

            const section = this.replyFormBase.cloneNode(true);
            section.dataset.dcx = `reply-form-${reply_to}`;

            // Update fields reply_to and cpage..
            const newForm = section.querySelector("form");
            newForm.elements.reply_to.value = reply_to;
            if (cpage) {
                newForm.elements[cpage_field].value = cpage;
            }

            elem.replaceWith(section);
            this.init(reply_to);
            this.replyMap.set(reply_to, section);
        }
    }

    init(reply_to, is_active) {
        const qs_section = `[data-dcx=reply-form-${reply_to}]`;
        const section = document.querySelector(qs_section);

        // Modify the form (update fields, add event listeners).
        const newForm = section.querySelector("form");
        const post_btn = newForm.elements.post;
        post_btn.addEventListener("click", this.send_clicked(reply_to));
        const preview_btn = newForm.elements.preview;
        preview_btn.addEventListener("click", this.preview_clicked(reply_to));
        const cancel_btn = newForm.elements.cancel;
        cancel_btn.addEventListener("click", this.cancel_clicked(reply_to));
        newForm.style.display = "none";

        // Attach event listener to textarea.
        const divta = section.querySelector("[data-dcx=reply-textarea]");
        const ta = divta.querySelector("textarea");
        ta.addEventListener("focus", this.textarea_focus(reply_to));

        // If is_active is true, hide the textarea and display the form.
        if (is_active === true) {
            section.classList.add("active");
            divta.style.display = "none";
            newForm.style = "";
            newForm.elements.comment.focus();
        }
    }

    get_map_item(reply_to) {
        const item = this.replyMap.get(reply_to);
        if (item === undefined) {
            const msg = `replyMap doesn't have a key ${reply_to}`;
            console.error(msg);
            throw msg;
        }
        return item;
    }

    disable_buttons(formEl, value) {
        formEl.elements.post.disabled = value;
        formEl.elements.preview.disabled = value;
    }

    is_valid(formEl) {
        for (const el of formEl.querySelectorAll("[required]")) {
            if (!el.reportValidity()) {
                return false;
            }
        }
        return true;
    }

    textarea_focus(reply_to) {
        // Display the comment form and hide the text area.
        return (_) => {
            const item = this.get_map_item(reply_to);
            const form = item.querySelector("form");
            const divta = item.querySelector("[data-dcx=reply-textarea]");
            item.classList.toggle("active");
            divta.style.display = "none";
            form.style = "";
            form.elements.comment.focus();
        };
    }

    cancel_clicked(reply_to) {
    // Display the text area and hide the comment form.
        return (_) => {
            const item = this.get_map_item(reply_to);
            const form = item.querySelector("form");
            const divta = item.querySelector("[data-dcx=reply-textarea]");
            const comment_value = form.elements.comment.value;
            divta.querySelector("textarea").value = comment_value;
            item.classList.toggle("active");
            form.style.display = "none";
            divta.style = "";

            const previewEl = item.querySelector("[data-dcx=preview]");
            if (previewEl) {
                previewEl.remove();
            }
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
        const formEl = item.querySelector("form");

        if (!this.is_valid(formEl)) {
            return;
        }

        this.disable_buttons(formEl, true);

        const previewEl = item.querySelector("[data-dcx=preview]");
        if (previewEl) {
            previewEl.remove();
        }

        const formData = new FormData(formEl);
        if (submit_button_name !== undefined) {
            formData.append(submit_button_name, 1);
        }

        fetch(formEl.action, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        }).then(response => {
            if (submit_button_name === "preview") {
                this.handle_preview_comment_response(response, reply_to);
            } else if (submit_button_name === "post") {
                this.handle_post_comment_response(response, reply_to);
            }
        });
        this.disable_buttons(formEl, false);
        return false; // To prevent calling the action attribute.
    }

    handle_http_200(item, data, reply_to) {
        const parent = item.parentNode;
        parent.innerHTML = data.html;
        const qs_section = `[data-dcx=reply-form-${reply_to}]`;
        const new_item = parent.querySelector(qs_section);
        this.replyMap.set(reply_to, new_item);
        this.init(reply_to, true); // 2nd param: is_active = true.
        if (data.field_focus) {
            new_item.querySelector(`[name=${data.field_focus}]`).focus();
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
