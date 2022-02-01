import fs from 'fs';
import path from 'path';

import {
    findByText, fireEvent, getByLabelText, getByPlaceholderText, getByRole,
    waitFor
} from '@testing-library/dom';
import '@testing-library/jest-dom/extend-expect';
import { JSDOM, ResourceLoader } from 'jsdom';

let dom;
let container;
let qs_cform;

const index_html_path = path.resolve(__dirname, './index.html');

const preview_form_wrong_email_200 = fs.readFileSync(
    path.resolve(__dirname, './preview_form_wrong_email_200.html')
).toString();

const preview_form_success_200 = fs.readFileSync(
    path.resolve(__dirname, './preview_form_success_200.html')
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

describe("comments.test.js module", () => {
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
                qs_cform = "[data-dcx=comment-form]";
                resolve();
            });
        });
    });

    it("asserts window.dcx.comment_form attributes", () => {
        expect(dom.window.dcx !== null && dom.window.dcx !== undefined);
        expect(dom.window.dcx.comment_form !== null);
        expect(dom.window.dcx.comment_form.formWrapper === qs_cform);

        const elem = container.querySelector(qs_cform);
        expect(dom.window.dcx.comment_form.formWrapperEl === elem);

        const form = elem.querySelector("form");
        expect(dom.window.dcx.comment_form.formEl === form);
    });

    it("previewing empty form focuses on textarea comment", () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const preview = getByRole(cFormWrapper, "button", {name: /preview/i});
        fireEvent.click(preview);
        const comment_ta = getByPlaceholderText(cFormWrapper, /your comment/i);
        expect(dom.window.document.activeElement).toEqual(comment_ta);
    });

    it("previewing form focuses on input name", () => {
        // This happens only when the comment textarea has content.
        const cFormWrapper = container.querySelector(qs_cform);
        const comment_ta = getByPlaceholderText(cFormWrapper, /your comment/i);
        fireEvent.change(comment_ta, {target: {value: "This is my comment"}});
        const preview = getByRole(cFormWrapper, "button", {name: /preview/i});
        fireEvent.click(preview);
        const name_field = getByLabelText(cFormWrapper, /name/i);
        expect(dom.window.document.activeElement).toEqual(name_field);
    });

    it("previewing form focuses on input email", () => {
        // This happens only when both comment and name fields have content.
        const cFormWrapper = container.querySelector(qs_cform);
        const comment_ta = getByPlaceholderText(cFormWrapper, /your comment/i);
        fireEvent.change(comment_ta, {target: {value: "This is my comment"}});
        const name_field = getByLabelText(cFormWrapper, /name/i);
        fireEvent.change(name_field, {target: {value: "Emma"}});
        const preview = getByRole(cFormWrapper, "button", {name: /preview/i});
        fireEvent.click(preview);
        const email_field = getByLabelText(cFormWrapper, /mail/i);
        expect(dom.window.document.activeElement).toEqual(email_field);
    });

    it("preview tampered form receives 400 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_form_with_wrong_email(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 400,
            json: () => Promise.resolve({
                html: post_form_receives_400
            })
        }));

        const preview = getByRole(formEl, "button", {name: /preview/i});
        fireEvent.click(preview);

        const formData = new dom.window.FormData(formEl);
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
            const qs = "[data-dcx=comment-form] form h6";
            const h6 = dom.window.document.querySelector(qs);
            expect(h6.textContent.indexOf("An error has happened.") > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("preview form with wrong email receives 200 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_form_with_wrong_email(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 200,
            json: () => Promise.resolve({
                html: preview_form_wrong_email_200,
                field_focus: "email"
            })
        }));

        const preview = getByRole(formEl, "button", {name: /preview/i});
        fireEvent.click(preview);

        const formData = new dom.window.FormData(formEl);
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

        await findByText(container, "Enter a valid email address.");
        const email_input = container.querySelector("form [name=email]");
        expect(dom.window.document.activeElement).toEqual(email_input);
        dom.window.fetch.mockClear();
    });

    it("preview form receives 200 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_valid_form(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 200,
            json: () => Promise.resolve({ html: preview_form_success_200 })
        }));

        const preview = getByRole(formEl, "button", {name: /preview/i});
        fireEvent.click(preview);

        const formData = new dom.window.FormData(formEl);
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
            expect(
                dom.window.document.querySelector("[data-dcx=preview]")
            ).toBeInTheDocument();
        });
        dom.window.fetch.mockClear();
    });

    it("post form receives 400 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_valid_form(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 400,
            json: () => Promise.resolve({ html: post_form_receives_400 })
        }));

        const send_btn = getByRole(formEl, "button", {name: /send/i});
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(formEl);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            }
        );

        await findByText(container, "An error has happened.");
        await findByText(container, "The comment form failed security verification.");
        await waitFor(() => {
            const qs = "[data-dcx=comment-form] form h6";
            const h6 = dom.window.document.querySelector(qs);
            expect(h6.textContent.indexOf("An error has happened.") > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("post form receives 201 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_valid_form(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({ html: post_form_receives_201 })
        }));

        const send_btn = getByRole(formEl, "button", {name: /send/i});
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(formEl);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            }
        );

        await findByText(container, "Comment published");
        await waitFor(() => {
            const qs = "[data-dcx=comment-form] form > div > div";
            const alert = dom.window.document.querySelector(qs);
            expect(alert.textContent.indexOf("Comment published") > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("post form receives 202 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_valid_form(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 202,
            json: () => Promise.resolve({ html: post_form_receives_202 })
        }));

        const send_btn = getByRole(formEl, "button", {name: /send/i});
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(formEl);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            }
        );

        const text = "Comment confirmation requested";
        await findByText(container, text);
        await waitFor(() => {
            const qs = "[data-dcx=comment-form] form > div > div";
            const alert = dom.window.document.querySelector(qs);
            expect(alert.textContent.indexOf(text) > -1);
        });
        dom.window.fetch.mockClear();
    });

    it("post form receives 500 response", async () => {
        const cFormWrapper = container.querySelector(qs_cform);
        const formEl = cFormWrapper.querySelector("form");
        prepare_valid_form(formEl);

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 500,
            json: () => Promise.resolve({})
        }));

        const alertMock = jest.spyOn(dom.window, 'alert').mockImplementation();

        const send_btn = getByRole(formEl, "button", {name: /send/i});
        fireEvent.click(send_btn);

        const formData = new dom.window.FormData(formEl);
        formData.append("post", 1);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "file:///comments/post/",
            {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
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
