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
function init_reactions() {
    const rroot = document.querySelector("[data-dcx=config]");
    if (rroot === null || window.dcx === null) {
        return;
    }

    /* ----------------------------------------------
     * Initialize dcx namespace values.
     */
    if (window.dcx.guest === undefined) {
        window.dcx.guest = rroot.getAttribute("data-guest-user");
    }
    window.dcx.login_url = init_login_url(rroot);
    window.dcx.react_url = init_react_url(rroot);

    /* ----------------------------------------------
     * Initialize the buttons panels and their components.
     */
    const links = document.querySelectorAll("[data-dcx=reactions-panel]");
    if (links.length === 0) {
        throw new Error("Cannot initialize reactions panel => There are no " +
            "elements with [data-dcx=reactions-panel].");
    }
    // create_buttons_panels(links, row_length, header_title);
    create_buttons_panels(links);

    /* ----------------------------------------------
     * Initialize reactions-tooltips.
     */
    document
        .querySelectorAll("[data-toggle=reactions-tooltip]")
        .forEach(node => {
            node.addEventListener("mouseover", on_mouseover_tooltip);
            node.addEventListener("mouseout", on_mouseout_tooltip);
        });
}

function init_login_url(elem) {
    const url = elem.getAttribute("data-login-url");
    if (url === null || url.length === 0) {
        if (window.dcx.guest && window.dcx.guest === "1") {
            throw new Error("Cannot initialize reactions panel => The " +
                "[data-login-url] attribute does not exist or is empty.");
        }
    }
    return url;
}

function init_react_url(elem) {
    const url = elem.getAttribute("data-react-url");
    if (url === null || url.length === 0) {
        if (window.dcx.guest && window.dcx.guest === "0") {
            throw new Error("Cannot initialize reactions panel => The " +
                "[data-react-url] attribute does not exist or is empty.");
        } else {
            console.info("Couldn't find the data-react-url attribute, " +
                "but the user is anonymous. She has to login first in order " +
                "to post comment reactions.");
        }
    }
    return url;
}

function toggle_buttons_panel(comment_id) {
    return (event) => {
        event.preventDefault();
        // Hide all the panels but the target.
        document.querySelectorAll(".reactions-panel").forEach(elem => {
            if (elem.getAttribute("data-crpanel") !== comment_id) {
                elem.style.display = "none";
            }
        });
        // Toggle the panel corresponding to the clicked link.
        const panel = document.querySelector(`[data-crpanel="${comment_id}"]`);
        if (panel) {
            if (panel.style.display !== "block") {
                panel.style.display = "block";
            } else {
                panel.style.display = "";
            }
        }
    };
}

function create_buttons_panels(nodes) {
    const qs_template = "[data-dcx=reactions-panel-template]";
    const template = document.querySelector(qs_template);

    for (const elem of Array.from(nodes)) {
        const comment_id = elem.getAttribute("data-comment");
        if (comment_id === null) {
            continue;
        }

        const panel = template.cloneNode(true);
        delete panel.dataset.dcx;
        panel.setAttribute("data-crpanel", `${comment_id}`);
        const header = panel.querySelector("h3");
        const header_title = header.textContent;
        const buttons = panel.querySelectorAll("P > BUTTON");

        for (const btn of Array.from(buttons)) {
            if (window.dcx.guest === "0") {
                btn.addEventListener("click", on_click_reaction_btn(btn.dataset.code, comment_id));
            } else {
                btn.addEventListener("click", function(_) {
                    window.location.href = (
                        `${window.dcx.login_url}?next=${login_next_url}`
                    );
                });
            }
            btn.addEventListener("mouseover", on_mouseover_reaction_btn(header));
            btn.addEventListener("mouseout", on_mouseout_reaction_btn(header, header_title));
        }

        elem.parentNode.insertBefore(panel, elem);
        calc_buttons_panel_position(comment_id);
        elem.addEventListener("click", toggle_buttons_panel(comment_id));
    }
}

function calc_buttons_panel_position(cid) {
    const panel = document.querySelector(`[data-crpanel="${cid}"]`);
    if (panel) {
        const rroot = document.querySelector("[data-dcx=config]");
        const bottom = parseInt(rroot.getAttribute("data-popover-pos-bottom")) || 0;
        const left = parseInt(rroot.getAttribute("data-popover-pos-left")) || 0;
        const elem_sel = `[data-dcx="reactions-panel"][data-comment="${cid}"]`;
        const elem = document.querySelector(elem_sel);
        // elem is the <a>React</a>, and elem.parentNode.parentNode is the
        // element containing the .active-reactions (reactions already
        // selected by users).
        const anchor_pos = elem.getBoundingClientRect();
        const footer_pos = elem.parentNode.parentNode.getBoundingClientRect();
        panel.style.bottom = `${bottom}px`;
        panel.style.left = `${anchor_pos.x - footer_pos.x - left}px`;
    }
}

function on_mouseover_reaction_btn(header) {
    return (event) => {
        header.textContent = event.target.getAttribute("data-title");
    };
}

function on_mouseout_reaction_btn(header, header_title) {
    return (_) => header.textContent = header_title;
}

function on_click_reaction_btn(crid, cid) {
    return (event) => {
        event.preventDefault();
        post_reaction({ comment: cid, reaction: crid }).then(data => {
            handle_reaction_response(cid, data);
        });
    };
}

function on_mouseover_tooltip(event) {
    const parent_all = event.target.parentNode.parentNode;
    const bottom = parseInt(parent_all.getAttribute("data-tooltip-pos-bottom")) || 0;
    const left = parseInt(parent_all.getAttribute("data-tooltip-pos-left")) || 0;
    const tooltip = event.target.parentNode.children[0];
    const target_pos = event.target.getBoundingClientRect();
    const parent_all_pos = parent_all.getBoundingClientRect();
    if (tooltip.className === "reactions-tooltip") {
        tooltip.style.display = "block";
        tooltip.style.bottom = `${bottom}px`;
        tooltip.style.left = `${target_pos.x - parent_all_pos.x - left}px`;
    }
}

function on_mouseout_tooltip(event) {
    const tooltip = event.target.parentNode.children[0];
    if (tooltip.className === "reactions-tooltip") {
        tooltip.style.display = "";
    }
}

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

async function post_reaction(data) {
    const response = await fetch(window.dcx.react_url, {
        method: "POST",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": get_cookie("csrftoken"),
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        redirect: "follow",
        referrerPolicy: "no-referrer",
        body: JSON.stringify(data)
    });
    return response.json();
}

function handle_reaction_response(cid, data) {
    const cm_footer = document.getElementById(`cm-footer-${cid}`);
    const cm_reactions_div = document.getElementById(`cm-reactions-${cid}`);
    if (data.counter > 0) {
        const new_list = create_reactions_list(data);
        if (cm_reactions_div === null) {
            const reactions = document.createElement("div");
            reactions.id = `cm-reactions-${cid}`;
            reactions.className = "reactions";
            reactions.appendChild(new_list);
            reactions.insertAdjacentHTML("beforeend", "&nbsp;");
            cm_footer.insertBefore(reactions, cm_footer.children[0]);
            reactions.insertAdjacentHTML("afterend", "&nbsp;");
        } else {
            const old_list = cm_reactions_div.querySelector(".active-reactions");
            cm_reactions_div.replaceChild(new_list, old_list);
        }
    } else if (cm_reactions_div) {
        cm_reactions_div.remove();
        for (const node of cm_footer.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
                node.textContent = "";
            }
        }
    }
    // Recalculate the position of the reactions buttons panel.
    calc_buttons_panel_position(cid);
}

function create_reactions_list(data) {
    const rroot = document.querySelector("[data-dcx=config]");
    const list = document.createElement("div");
    list.className = "active-reactions";
    list.setAttribute("data-tooltip-pos-bottom", rroot.getAttribute("data-tooltip-pos-bottom"));
    list.setAttribute("data-tooltip-pos-left", rroot.getAttribute("data-tooltip-pos-left"));
    for (const item of data.list) {
        const reaction = document.createElement("span");
        reaction.className = "reaction";
        reaction.dataset.reaction = item.value;
        reaction.appendChild(create_tooltip(item));
        const anchor = document.createElement("a");
        anchor.className = "small text-primary";
        anchor.setAttribute("data-toggle", "reactions-tooltip");
        anchor.addEventListener("mouseover", on_mouseover_tooltip);
        anchor.addEventListener("mouseout", on_mouseout_tooltip);
        anchor.appendChild(document.createTextNode(`${item.counter}`));
        const emoji = document.createElement("span");
        emoji.className = "emoji";
        emoji.innerHTML = `&${item.icon};`;
        anchor.appendChild(emoji);
        reaction.appendChild(anchor);
        list.appendChild(reaction);
    }
    return list;
}

function create_tooltip(reaction) {
    const tooltip = document.createElement("div");
    tooltip.className = "reactions-tooltip";
    const arrow = document.createElement("div");
    arrow.className = "arrow";
    tooltip.appendChild(arrow);
    const p = document.createElement("p");
    p.textContent = `${reaction.authors.join(", ")} ` +
        `reacted with ${reaction.label}`;
    tooltip.appendChild(p);
    return tooltip;
}

/* ------------------------------------------------------------------------
 * Initialize the module when the page is loaded.
 *
 * Also, reactions panels must close when the user clicks outside of them,
 * or when the user hits the ESC key.
 */
window.addEventListener("mouseup", (event) => {
    const data_attr = event.target.getAttribute("data-dcx");
    if (data_attr !== "reactions-panel") {
        // Clicking outside the "React" link must close the reactions panel.
        document.querySelectorAll(".reactions-panel").forEach(elem => {
            elem.style.display = "none";
        });
    }
});

window.addEventListener("keyup", (event) => {
    if (event.key === "Escape") {
        document.querySelectorAll(".reactions-panel").forEach(elem => {
            elem.style.display = "none";
        });
    }
});




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