export default class CommentForm {
    constructor(formWrapper) {
        this.formWrapper = formWrapper;
        this.init();
    }

    click_on_post(_) { return this.post("post"); }

    click_on_preview(_) { return this.post("preview"); }

    init() {
        this.formWrapperEl = document.querySelector(this.formWrapper);
        this.formEl = this.formWrapperEl.querySelector("form");
        const post_btn = this.formEl.elements.post;
        const preview_btn = this.formEl.elements.preview;
        post_btn.addEventListener("click", (_) => this.post("post"));
        preview_btn.addEventListener("click", (_) => this.post("preview"));
        // Change the type of the buttons, otherwise the form is submitted.
        post_btn.type = "button";
        preview_btn.type = "button";
    }

    disable_btns(value) {
        this.formEl.elements.post.disabled = value;
        this.formEl.elements.preview.disabled = value;
    }

    is_valid() {
        for (const el of this.formEl.querySelectorAll("[required]")) {
            if (!el.reportValidity()) {
                el.focus();
                return false;
            }
        }
        return true;
    }

    post(submit_button_name) {
        if (!this.is_valid()) {
            return;
        }
        this.disable_btns(true);

        // If the <section data-dcx="preview">...</section> does exist,
        // delete it. If the user clicks again in the "preview" button
        // it will be displayed again.
        const preview = this.formWrapperEl.querySelector("[data-dcx=preview]");
        if (preview) {
            preview.remove();
        }

        const formData = new FormData(this.formEl);
        if (submit_button_name !== undefined) {
            formData.append(submit_button_name, 1);
        }

        fetch(this.formEl.action, {
            method: 'POST',
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        }).then(response => {
            if (submit_button_name === "preview") {
                this.handle_preview_comment_response(response);
            } else if (submit_button_name === "post") {
                this.handle_post_comment_response(response);
            }
        });

        this.disable_btns(false);
        return false; // To prevent calling the action attribute.
    }

    async handle_preview_comment_response(response) {
        const data = await response.json();
        if (response.status === 200) {
            this.formWrapperEl.innerHTML = data.html;
            this.init();
            if (data.field_focus) {
                this.formEl.querySelector(`[name=${data.field_focus}]`).focus();
            }
        } else if (response.status === 400) {
            this.formEl.innerHTML = data.html;
        }
    }

    async handle_post_comment_response(response) {
        const data = await response.json();

        if (response.status === 200) {
            this.formWrapperEl.innerHTML = data.html;
            this.init();
            if (data.field_focus) {
                this.formEl.querySelector(`[name=${data.field_focus}]`).focus();
            }
        }
        else if (
            response.status === 201 ||
            response.status === 202 ||
            response.status === 400
        ) {
            this.formEl.innerHTML = data.html;
        }
        else if (response.status > 400) {
            alert(
                "Something went wrong and your comment could not be " +
                "processed. Please, reload the page and try again."
            );
        }
    }
}
