/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./django_comments_xtd/static/django_comments_xtd/js/comment_form.js":
/*!***************************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/comment_form.js ***!
  \***************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ CommentForm)
/* harmony export */ });
class CommentForm {
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


/***/ }),

/***/ "./django_comments_xtd/static/django_comments_xtd/js/comments.js":
/*!***********************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/comments.js ***!
  \***********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "init_comments": () => (/* binding */ init_comments)
/* harmony export */ });
/* harmony import */ var _comment_form_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./comment_form.js */ "./django_comments_xtd/static/django_comments_xtd/js/comment_form.js");
/* harmony import */ var _reply_forms_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./reply_forms.js */ "./django_comments_xtd/static/django_comments_xtd/js/reply_forms.js");




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
        window.dcx.comment_form = new _comment_form_js__WEBPACK_IMPORTED_MODULE_0__["default"](qs_cform);
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
        window.dcx.reply_forms_handler = new _reply_forms_js__WEBPACK_IMPORTED_MODULE_1__["default"](qs_rform_base, qs_rforms);
    }
}




/***/ }),

/***/ "./django_comments_xtd/static/django_comments_xtd/js/reactions.js":
/*!************************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/reactions.js ***!
  \************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "init_reactions": () => (/* binding */ init_reactions)
/* harmony export */ });
/* harmony import */ var _reactions_handler__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./reactions_handler */ "./django_comments_xtd/static/django_comments_xtd/js/reactions_handler.js");


function init_reactions() {
    if (window.dcx === null) {
        return;
    }

    const rroot = document.querySelector("[data-dcx=config]");
    if (rroot === null || window.dcx === null) {
        return;
    }

    window.dcx.reactions_handler = null;

    /* ----------------------------------------------
     * Initialize reactions_handler, in charge
     * of all reactions popover components.
     */
    if (window.dcx.reactions_handler === null) {
        window.dcx.reactions_handler = new _reactions_handler__WEBPACK_IMPORTED_MODULE_0__["default"](rroot);
        window.addEventListener("beforeunload", (_) => {
            console.log(`About to call reactions_handler.remove_events()`);
            window.dcx.reactions_handler.remove_event_listeners();
        });

    }
}




/***/ }),

/***/ "./django_comments_xtd/static/django_comments_xtd/js/reactions_handler.js":
/*!********************************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/reactions_handler.js ***!
  \********************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ReactionsHandler)
/* harmony export */ });
/* harmony import */ var _reactions_panel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./reactions_panel */ "./django_comments_xtd/static/django_comments_xtd/js/reactions_panel.js");


class ReactionsHandler {
    constructor(configEl) {
        this.cfg_el = configEl;
        this.is_guest = this.cfg_el.getAttribute("data-guest-user") === "1";
        this.login_url = this.init_login_url();
        this.react_url = this.init_react_url();

        // Initialize the buttons panels and their components.
        this.links = document.querySelectorAll("[data-dcx=reactions-panel]");
        if (this.links.length === 0) {
            throw new Error(
                "Cannot initialize reactions panel => There are " +
                "no elements with [data-dcx=reactions-panel].");
        }
        this.active_visible_panel = 0;
        this.panels_visibility = new Map(); // Keys are 'comment_id'.
        this.event_handlers = [];
        this.add_event_listeners();
        this.listen_to_click_on_links();
        const qs_panel = "[data-dcx=reactions-panel-template]";
        this.panel_el = document.querySelector(qs_panel);
        if (this.panel_el === undefined) {
            throw new Error("Cannot find element with ${qs_panel}.");
        }

        // Create object of class ReactionsPanel in charge of showing and
        // hiding the reactions panel around the clicked 'react' link.
        const opts = {
            panel_el: this.panel_el,
            is_guest: this.is_guest,
            login_url: this.login_url,
            react_url: this.react_url
        };
        this.reactions_panel = new _reactions_panel__WEBPACK_IMPORTED_MODULE_0__["default"](opts);
    }

    init_login_url() {
        const url = this.cfg_el.getAttribute("data-login-url");
        if (url === null || url.length === 0) {
            if (this.is_guest) {
                throw new Error("Cannot initialize reactions panel => The " +
                    "[data-login-url] attribute does not exist or is empty.");
            }
        }
        return url;
    }

    init_react_url() {
        const url = this.cfg_el.getAttribute("data-react-url");
        if (url === null || url.length === 0) {
            if (!this.is_guest) {
                throw new Error("Cannot initialize reactions panel => The " +
                    "[data-react-url] attribute does not exist or is empty.");
            } else {
                console.info("Couldn't find the data-react-url attribute, " +
                    "but the user is anonymous. She has to login first in " +
                    "order to post comment reactions.");
            }
        }
        return url;
    }

    on_document_click(event) {
        const data_attr = event.target.getAttribute("data-dcx");
        if (!data_attr || data_attr !== "reactions-panel") {
            this.reactions_panel.hide();
            if (this.active_visible_panel) {
                console.log(`reactions off: ${this.active_visible_panel}`);
                this.panels_visibility.set(this.active_visible_panel, false);
                this.active_visible_panel = 0;
            }
        }
    }

    on_document_key_up(event) {
        if (event.key === "Escape") {
            this.reactions_panel.hide();
            if (this.active_visible_panel) {
                console.log(`reactions off: ${this.active_visible_panel}`);
                this.panels_visibility.set(this.active_visible_panel, false);
                this.active_visible_panel = 0;
            }
        }
    }

    add_event_listeners() {
        const onDocumentClickHandler = this.on_document_click.bind(this);
        const onDocumentKeyUpHandler = this.on_document_key_up.bind(this);

        window.document.addEventListener('click', onDocumentClickHandler);
        window.document.addEventListener('keyup', onDocumentKeyUpHandler);

        this.event_handlers.push({
            elem: window.document,
            event: 'click',
            handler: this.on_document_click,
        });
        this.event_handlers.push({
            elem: window.document,
            event: 'keyup',
            handler: this.on_document_key_up,
        });
    }

    remove_event_listeners() {
        console.log(`Removing events...`);
        for (const item of this.event_handlers) {
            item.elem.removeEventListener(item.event, item.handler);
        }
    }

    listen_to_click_on_links() {
        for (const elem of Array.from(this.links)) {
            const comment_id = elem.getAttribute("data-comment");
            if (comment_id === null) {
                continue;
            }
            const click_handler = this.toggle_reactions_panel(comment_id);
            elem.addEventListener("click", click_handler);
            this.event_handlers.push({
                'elem': elem,
                'event': 'click',
                'handler': click_handler
            });
            this.panels_visibility.set(comment_id, false); // Not visible yet.
        }
    }

    toggle_reactions_panel(comment_id) {
        return (event) => {
            event.preventDefault();
            const is_visible = this.panels_visibility.get(comment_id);
            if (!is_visible) {
                this.active_visible_panel = comment_id;
                this.reactions_panel.show(event.target, comment_id);
            } else {
                this.active_visible_panel = 0;
                this.reactions_panel.hide();
            }
            this.panels_visibility.set(comment_id, !is_visible);
        };
    }
}


/***/ }),

/***/ "./django_comments_xtd/static/django_comments_xtd/js/reactions_panel.js":
/*!******************************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/reactions_panel.js ***!
  \******************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ReactionsPanel)
/* harmony export */ });
const enter_delay = 0;
const exit_delay = 0;

function get_cookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class ReactionsPanel {
    constructor({panel_el, is_guest, login_url, react_url } = opts) {
        this.panel_el = panel_el;
        // this.panel_el.style.zIndex = 1;
        // this.panel_el.style.display = "block";
        this.arrow_el = panel_el.querySelector(".arrow");
        this.is_guest = is_guest;
        this.login_url = login_url;
        this.react_url = react_url;

        // -----------------------------------------------------
        // The panel_title_elem and its content panel_title will
        // change when the user hover the buttons of the panel.

        this.panel_title = "";
        this.panel_title_elem = this.panel_el.querySelector(".title");
        if (this.panel_title_elem) {
            this.panel_title = this.panel_title_elem.textContent;
        }

        // -----------------------------------------
        // The comment_id is necessary to know which
        // comment will receive the reaction code.

        this.comment_id = 0; // Valid comment_id must be > 0.
        this.next_url = ""; // Comment URL to come back after log in.

        this.on_react_btn_click = this.on_react_btn_click.bind(this);
        this.on_react_btn_mouseover = this.on_react_btn_mouseover.bind(this);
        this.on_react_btn_mouseout = this.on_react_btn_mouseout.bind(this);
        this.add_event_listeners();
    }

    add_event_listeners() {
        const buttons = this.panel_el.querySelectorAll("BUTTON");
        console.log(`Found ${buttons.length} buttons`);
        for (const btn of Array.from(buttons)) {
            btn.addEventListener("click", this.on_react_btn_click);
            btn.addEventListener("mouseover", this.on_react_btn_mouseover);
            btn.addEventListener("mouseout", this.on_react_btn_mouseout);
        }
    }

    on_react_btn_click(event) {
        if (!this.is_guest) {
            const code = event.target.dataset.code;
            const react_url = this.react_url.replace("0", this.comment_id);
            const formData = new FormData();
            formData.append("reaction", code);
            formData.append("csrfmiddlewaretoken", get_cookie("csrftoken"));
            fetch(react_url, {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }).then(response => this.handle_reactions_response(response));
        } else {
            window.location.href = `${this.login_url}?next=${this.next_url}`;
        }
    }

    async handle_reactions_response(response) {
        const data = await response.json();
        if (response.status === 200 || response.status === 201) {
            const cm_reactions_qs = `#cm-reactions-${this.comment_id}`;
            const cm_reactions_el = document.querySelector(cm_reactions_qs);
            if (cm_reactions_el) {
                cm_reactions_el.innerHTML = data.html;
            }
        } else if (response.status > 400) {
            alert(
                "Something went wrong and your comment reaction could not " +
                "be processed. Please, reload the page and try again."
            );
        }
    }

    on_react_btn_mouseover(event) {
        console.log(`on_react_btn_mouseover:`, event.target.dataset.title);
        if (this.panel_title_elem) {
            this.panel_title_elem.textContent = event.target.dataset.title;
        }
    }

    on_react_btn_mouseout(_) {
        this.panel_title_elem.textContent = this.panel_title;
    }

    set_position(trigger_elem) {
        this.panel_el.style.display = "block";

        const panel_elem_coords = this.get_absolute_coords(this.panel_el);
        const trigger_elem_coords = this.get_absolute_coords(trigger_elem);

        const panel_elem_width = panel_elem_coords.width;
        const panel_elem_height = panel_elem_coords.height;
        const panel_elem_top = panel_elem_coords.top;
        const panel_elem_left = panel_elem_coords.left;

        const trigger_elem_width = trigger_elem_coords.width;
        const trigger_elem_top = trigger_elem_coords.top;
        const trigger_elem_left = trigger_elem_coords.left;

        const top_diff = trigger_elem_top - panel_elem_top;
        const left_diff = trigger_elem_left - panel_elem_left;

        // This group of const values can be hardcoded somewhere else.
        // const position = "auto";
        const margin = 8;

        const width_center = trigger_elem_width / 2 - panel_elem_width / 2;

        const left = left_diff + width_center;
        const top = top_diff - panel_elem_height - margin;
        const from_top = top + 10;

        this.panel_el.dataset.fromLeft = left;
        this.panel_el.dataset.fromTop = from_top;
        this.panel_el.dataset.left = left;
        this.panel_el.dataset.top = top;

        // Arrow.
        if (this.arrow_el) {
            let arrow_left = 0;
            const full_left = left + panel_elem_left;
            const t_width_center = trigger_elem_width / 2 + trigger_elem_left;
            arrow_left = t_width_center - full_left;
            const transform_text = `translate3d(${arrow_left}px, 0px, 0)`;
            this.arrow_el.style.transform = transform_text;
        }
    }

    hide() {
        clearTimeout(this.enter_delay_timeout);

        this.exit_delat_timeout = setTimeout(() => {
            if (this.panel_el) {
                const left = this.panel_el.dataset.fromLeft;
                const top = this.panel_el.dataset.fromTop;
                const transform_text = `translate3d(${left}px, ${top}px, 0)`;

                this.panel_el.style.transform = transform_text;
                this.panel_el.style.opacity = 0;
                this.panel_el.style.display = "none";
                this.panel_el.style.zIndex = 0;
            }
        }, exit_delay);
    }

    show(trigger_elem, comment_id) {
        this.comment_id = comment_id;
        this.next_url = trigger_elem.dataset.loginNext || "";
        this.panel_el.style.transform = "none";
        this.set_position(trigger_elem);

        this.enter_delay_timeout = setTimeout(() => {
            const left = this.panel_el.dataset.left;
            const top = this.panel_el.dataset.top;
            const transform_text = `translate3d(${left}px, ${top}px, 0)`;

            this.panel_el.style.zIndex = 1;
            this.panel_el.style.display = "block";
            this.panel_el.style.transform = transform_text;
            this.panel_el.style.opacity = 1;
        }, enter_delay);
    }

    get_absolute_coords(elem) {
        if (!elem) {
            return;
        }

        const box = elem.getBoundingClientRect();
        const page_x = window.pageXOffset;
        const page_y = window.pageYOffset;

        return {
            width: box.width,
            height: box.height,
            top: box.top + page_y,
            right: box.right + page_x,
            bottom: box.bottom + page_y,
            left: box.left + page_x,
        };
    }
}


/***/ }),

/***/ "./django_comments_xtd/static/django_comments_xtd/js/reply_forms.js":
/*!**************************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/reply_forms.js ***!
  \**************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ReplyFormsHandler)
/* harmony export */ });
class ReplyFormsHandler {
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

            const elemParent = elem.parentNode;
            elem.replaceWith(section);
            this.init(reply_to);
            this.replyMap.set(reply_to, elemParent);
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
                el.focus();
                return false;
            }
        }
        return true;
    }

    textarea_focus(reply_to) {
        // Display the comment form and hide the text area.
        return (_) => {
            const item = this.get_map_item(reply_to);
            const qs_section = `[data-dcx=reply-form-${reply_to}`;
            const section = item.querySelector(qs_section);
            const form = section.querySelector("form");
            const divta = section.querySelector("[data-dcx=reply-textarea]");
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
            const qs_section = `[data-dcx=reply-form-${reply_to}`;
            const section = item.querySelector(qs_section);
            const form = section.querySelector("form");
            const divta = section.querySelector("[data-dcx=reply-textarea]");
            const comment_value = form.elements.comment.value;
            divta.querySelector("textarea").value = comment_value;
            section.classList.toggle("active");
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


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
/*!********************************************************************!*\
  !*** ./django_comments_xtd/static/django_comments_xtd/js/index.js ***!
  \********************************************************************/
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _comments_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./comments.js */ "./django_comments_xtd/static/django_comments_xtd/js/comments.js");
/* harmony import */ var _reactions_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./reactions.js */ "./django_comments_xtd/static/django_comments_xtd/js/reactions.js");



window.dcx.init_comments = _comments_js__WEBPACK_IMPORTED_MODULE_0__.init_comments;
window.dcx.init_reactions = _reactions_js__WEBPACK_IMPORTED_MODULE_1__.init_reactions;

window.addEventListener("DOMContentLoaded", (_) => {
    if (window.dcx === null) {
        return;
    }

    (0,_comments_js__WEBPACK_IMPORTED_MODULE_0__.init_comments)();
    (0,_reactions_js__WEBPACK_IMPORTED_MODULE_1__.init_reactions)();
});

})();

/******/ })()
;
//# sourceMappingURL=dcx-3.0.0.js.map