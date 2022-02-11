import fs from 'fs';
import path from 'path';

import {
    findByText, fireEvent, getByLabelText, getByPlaceholderText, getByText,
    waitFor
} from '@testing-library/dom';
import { JSDOM, ResourceLoader } from 'jsdom';

let dom;
let container;
let qs_rform_base;

const index_html_path = path.resolve(__dirname, './index.html');

const preview_reply_form_wrong_email_200 = fs.readFileSync(
    path.resolve(__dirname, './preview_reply_form_wrong_email_200.html')
).toString();

const preview_reply_form_success_200 = fs.readFileSync(
    path.resolve(__dirname, './preview_reply_form_success_200.html')
).toString();

const post_form_receives_400 = fs.readFileSync(
    path.resolve(__dirname, './post_form_receives_400.html')
).toString();

const post_form_receives_201 = fs.readFileSync(
    path.resolve(__dirname, './post_form_receives_201.html')
).toString();

const post_form_receives_202 = fs.readFileSync(
    path.resolve(__dirname, './post_form_receives_202.html')
).toString();

function prepare_form_with_wrong_email(formEl) {
    const comment_ta = getByPlaceholderText(formEl, /your comment/i);
    fireEvent.change(comment_ta, {target: {value: "This is my comment"}});
    const name_field = getByLabelText(formEl, /name/i);
    fireEvent.change(name_field, {target: {value: "Emma"}});
    const email_field = getByLabelText(formEl, /mail/i);
    // Feed the email field with a non-valid email address.
    fireEvent.change(email_field, {target: {value: "emma"}});
}

function prepare_valid_form(formEl) {
    const comment_ta = getByPlaceholderText(formEl, /your comment/i);
    fireEvent.change(comment_ta, {target: {value: "This is my comment"}});
    const name_field = getByLabelText(formEl, /name/i);
    fireEvent.change(name_field, {target: {value: "Emma"}});
    const email_field = getByLabelText(formEl, /mail/i);
    fireEvent.change(email_field, {target: {value: "emma@example.com"}});
}

describe("scene 2 - reply_forms.test.js module", () => {
    beforeEach(async () => {
        const resourceLoader = new ResourceLoader({
            proxy: "http://localhost:3000",
            strictSSL: false
        });
        const opts = { runScripts: "dangerously", resources: resourceLoader };
        dom = await JSDOM.fromFile(index_html_path, opts);
        await new Promise(resolve => {
            dom.window.addEventListener("DOMContentLoaded", () => {
                container = dom.window.document.body;
                qs_rform_base = "[data-dcx=reply-form-template]";
                resolve();
            })
        })
    });

    it("asserts window.dcx.reply_forms_handle attributes", () => {
        expect(dom.window.dcx !== null && dom.window.dcx !== undefined);
        expect(dom.window.dcx.reply_forms_handler !== null);
        expect(dom.window.dcx.reply_forms_handler.replyFormBase !== null);
        expect(dom.window.dcx.reply_forms_handler.replyMap !== null);

        const elem = container.querySelector(qs_rform_base);
        expect(dom.window.dcx.reply_forms_handler.replyFormBase === elem);

        expect(dom.window.dcx.reply_forms_handler.replyMap.size === 1);
    });

    it("asserts reply form is not visible until reply field clicked", () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        fireEvent.click(reply_ta);
        expect(reply_form.style.display === "");
        expect(reply_ta.style.display === "none");
    });

    it("focuses on reply-form's textarea comment when click on preview", () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        // Get the 'preview' button and click on it.
        const preview = reply_form.querySelector("button[name=preview]");
        fireEvent.click(preview);

        // Get the textarea within the reply-form containing
        // the comment and assert it got focused.
        const comment_ta = reply_form.querySelector("textarea[name=comment]");
        expect(dom.window.document.activeElement).toEqual(comment_ta);
    });

    it("focuses on reply-form's input name when click on preview", () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        // Get the reply-form textarea element and
        // change it so that it contains a comment.
        const comment_ta = reply_form.querySelector("textarea[name=comment]");
        fireEvent.change(comment_ta, {target: {value: "This is my comment"}});

        // Get the 'preview' button and click on it.
        const preview = reply_form.querySelector("button[name=preview]");
        fireEvent.click(preview);

        // Get the textarea within the reply-form containing
        // the comment and assert it got focused.
        const name_field = reply_form.querySelector("input[name=name]");
        expect(dom.window.document.activeElement).toEqual(name_field);
    });

    it("focuses on reply-form's input email when click on preview", () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        // Get the reply-form textarea element and change it so that it
        // contains a comment. Also get the input field 'name' and change it
        // so that it has a value.
        const comment_ta = reply_form.querySelector("textarea[name=comment]");
        fireEvent.change(comment_ta, {target: {value: "This is my comment"}});
        const name_field = reply_form.querySelector("input[name=name]");
        fireEvent.change(name_field, {target: {value: "Emma"}});

        // Get the 'preview' button and click on it.
        const preview = reply_form.querySelector("button[name=preview]");
        fireEvent.click(preview);

        // Get the textarea within the reply-form containing
        // the comment and assert it got focused.
        const email_field = reply_form.querySelector("input[name=email]");
        expect(dom.window.document.activeElement).toEqual(email_field);
    });

    it("receives http-400 when previewing a tampered form", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_form_with_wrong_email(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 400,
            json: () => Promise.resolve({
                html: post_form_receives_400
            })
        }));

        const preview = reply_form.querySelector("button[name=preview]");
        fireEvent.click(preview);

        const formData = new dom.window.FormData(reply_form);
        formData.append("preview", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await findByText(container, "An error has happened.");
        await findByText(container, "The comment form failed security verification.");
        await waitFor(() => {
            const qs = "[data-dcx=reply-form-902] form h6";
            const h6 = dom.window.document.querySelector(qs);
            expect(h6.textContent.indexOf("An error has happened.") > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("receives http-200 when previewing form with wrong email", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_form_with_wrong_email(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 200,
            json: () => Promise.resolve({
                html: preview_reply_form_wrong_email_200,
                field_focus: "email"
            })
        }));

        const preview = reply_form.querySelector("button[name=preview]");
        fireEvent.click(preview);

        const formData = new dom.window.FormData(reply_form);
        formData.append("preview", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        let new_rform;
        await waitFor(() => {
            const qs_rform = qs_reply_section + " form";
            expect(dom.window.document.querySelector(qs_rform));
            new_rform = dom.window.document.querySelector(qs_rform);
            getByText(new_rform, "Enter a valid email address.");
        });
        const email_input = new_rform.querySelector("form [name=email]");
        expect(dom.window.document.activeElement).toEqual(email_input);
        dom.window.fetch.mockClear();
    });

    it("receives http-200 when previewing reply form", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_valid_form(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 200,
            json: () => Promise.resolve({
                html: preview_reply_form_success_200,
            })
        }));

        const preview = reply_form.querySelector("button[name=preview]");
        fireEvent.click(preview);

        const formData = new dom.window.FormData(reply_form);
        formData.append("preview", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await waitFor(() => {
            expect(dom.window.document.querySelector("[data-dcx=preview]"));
        });
        dom.window.fetch.mockClear();
    });

    it("receives http-400 when submitting the reply form", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_valid_form(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 400,
            json: () => Promise.resolve({ html: post_form_receives_400 })
        }));

        const send_btn = reply_form.querySelector("button[name=post]");
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(reply_form);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await findByText(container, "An error has happened.");
        await findByText(container, "The comment form failed security verification.");
        await waitFor(() => {
            const qs = "[data-dcx=reply-form-902] form h6";
            const h6 = dom.window.document.querySelector(qs);
            expect(h6.textContent.indexOf("An error has happened.") > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("receives http-201 when submitting the reply form", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_valid_form(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({ html: post_form_receives_201 })
        }));

        const send_btn = reply_form.querySelector("button[name=post]");
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(reply_form);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await findByText(container, "Comment published");
        await waitFor(() => {
            const qs = "[data-dcx=reply-form-902] form > div > div";
            const alert = dom.window.document.querySelector(qs);
            expect(alert.textContent.indexOf("Comment published") > -1);
        });

        dom.window.fetch.mockClear();
    });

    it("receives http-202 when submitting the reply form", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_valid_form(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 202,
            json: () => Promise.resolve({ html: post_form_receives_202 })
        }));

        const send_btn = reply_form.querySelector("button[name=post]");
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(reply_form);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        const text = "Comment confirmation requested";
        await findByText(container, text);
        await waitFor(() => {
            const qs = "[data-dcx=reply-form-902] form > div > div";
            const alert = dom.window.document.querySelector(qs);
            expect(alert.textContent.indexOf(text) > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("receives http-500 when submitting the reply form", async () => {
        const qs_reply_section = "[data-dcx=reply-form-902]";
        const section = container.querySelector(qs_reply_section);
        const reply_form = section.querySelector("form");
        const reply_ta = section.querySelector("[data-dcx=reply-textarea]");

        // Assert that before it's clicked the
        // form is not visible but the field is.
        expect(reply_form.style.display === "none");
        expect(reply_ta.style.display === "");

        // Fire event to display reply-form and hide reply TA.
        fireEvent.click(reply_ta);

        prepare_valid_form(reply_form);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 500,
            json: () => Promise.resolve({})
        }));

        const send_btn = reply_form.querySelector("button[name=post]");
        fireEvent.click(send_btn);

        const alertMock = jest.spyOn(dom.window, 'alert').mockImplementation();

        const formData = new dom.window.FormData(reply_form);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await waitFor(() => {
            expect(alertMock).toHaveBeenCalledTimes(1);
        });
        dom.window.fetch.mockClear();
        alertMock.mockClear();
    });
});
