import path from 'path';

import {
    fireEvent, waitFor,
} from '@testing-library/dom';
import '@testing-library/jest-dom/extend-expect';
import { JSDOM, ResourceLoader } from 'jsdom';


const html_path = path.resolve(__dirname, './index.html');

let dom;
let container;

describe("scene 3 - reactions.test.js module", () => {
    beforeEach(async () => {
        const resourceLoader = new ResourceLoader({
            proxy: "http://localhost:3000",
            strictSSL: false
        });
        const opts = { runScripts: "dangerously", resources: resourceLoader };
        dom = await JSDOM.fromFile(html_path, opts);
        await new Promise(resolve => {
            dom.window.addEventListener("DOMContentLoaded", () => {
                // dom.window.dcx.init_reactions();
                container = dom.window.document.body;
                resolve();
            });
        });
    });

    it("makes window.dcx.comment_form attribute !== null", () => {
        expect(dom.window.dcx !== null && dom.window.dcx !== undefined);
        expect(dom.window.dcx.guest === "0");
        expect(dom.window.dcx.login_url === null);
        expect(dom.window.dcx.react_url === "/comments/api/react/");
    });

    it("has a div with [data-dcx=config] with more data attributes", () => {
        const qs_config = "[data-dcx=config]";
        const config_el = container.querySelector(qs_config);
        expect(config_el !== null);
        expect(config_el.dataset.react_url === "/comments/api/react/");
        expect(config_el.dataset.guest_user === "0");
        expect(config_el.dataset.popover_pos_bottom === "30");
        expect(config_el.dataset.popover_pos_left === "10");
        expect(config_el.dataset.tooltip_pos_bottom === "30");
        expect(config_el.dataset.tooltip_pos_left === "76");
        expect(config_el.dataset.page_qs_param === "cpage");
    });

    it("has a div#comment-29 with a [data-crpanel=29]", () => {
        const panel_qs = '[data-crpanel="29"]';
        const react_anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el !== null);

        const reactions_panel_el = comment_el.querySelector(panel_qs);
        expect(reactions_panel_el !== null);
    });

    it("opens/closes reactions panel by clicking on 'react' link", async() => {
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el != null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el != null);

        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            const hdler = dom.window.dcx.reactions_handler;
            expect(hdler.active_visible_panel === '29');
            expect(hdler.reactions_panel.comment_id === '29');
            expect(hdler.reactions_panel.panel_el.style.opacity == '1')
        });

        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            const hdler = dom.window.dcx.reactions_handler;
            expect(hdler.active_visible_panel === '0');
            expect(hdler.reactions_panel.comment_id === '29');
            expect(hdler.reactions_panel.panel_el.style.opacity == '0');
        });
    });

    it("clicks on the 'Like' and displays the 'Like'", async () => {
        const panel_qs = "[data-dcx=reactions-panel-template]";
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el != null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el != null);

        const reactions_panel_el = container.querySelector(panel_qs);
        expect(reactions_panel_el != null);

        // Click on the 'react' link to open the reactions panel.
        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            const hdler = dom.window.dcx.reactions_handler;
            expect(hdler.active_visible_panel === '29');
            expect(hdler.reactions_panel.comment_id === '29');
            expect(hdler.reactions_panel.panel_el.style.opacity == '1')
        });

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({
                html: "<div class=\"active-reactions\"><div class=\"reaction\" data-reaction=\"+\"><span class=\"smaller\">1</span><span class=\"emoji\">&#128077;</span><div class=\"reaction_tooltip\">Daniela Rushmore reacted with Like</div></div></div>",
                reply_to: "0"
            })
        }));
        // Get the like button element, and click on it.
        const like_btn_qs = "button[data-code='+']";
        const like_btn_el = reactions_panel_el.querySelector(like_btn_qs);
        expect(like_btn_el != undefined);
        fireEvent.click(like_btn_el);

        const formData = new dom.window.FormData();
        formData.append("reaction", "+");
        formData.append("csrfmiddlewaretoken", null);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/react/29/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await waitFor(() => {
            const feedback_qs = '#cm-feedback-29';
            const reaction_qs = '[data-reaction="+"]';

            // The feedback element does exist and has two direct children.
            const feedback_el = comment_el.querySelector(feedback_qs);
            expect(feedback_el != null);
            expect(feedback_el.children.length === 2);

            // The like reaction element does exist too.
            const like_reaction_el = comment_el.querySelector(reaction_qs);
            expect(like_reaction_el != null);
            expect(like_reaction_el.children[0].textContent === '1');
            expect(like_reaction_el.children[1].textContent === '👍');
        });

        dom.window.fetch.mockClear();
    });

    it("clicks on the 'Like' to add and remove the 'Like'", async () => {
        const panel_qs = '[data-dcx=reactions-panel-template]';
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el != null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el != null);

        const reactions_panel_el = container.querySelector(panel_qs);
        expect(reactions_panel_el != null);

        // Click on the 'react' link to open the reactions panel.
        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            const hdler = dom.window.dcx.reactions_handler;
            expect(hdler.active_visible_panel === '29');
            expect(hdler.reactions_panel.comment_id === '29');
            expect(hdler.reactions_panel.panel_el.style.opacity == '1')
        });

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({
                html: "<div class=\"active-reactions\"><div class=\"reaction\" data-reaction=\"+\"><span class=\"smaller\">1</span><span class=\"emoji\">&#128077;</span><div class=\"reaction_tooltip\">Daniela Rushmore reacted with Like</div></div></div>",
                reply_to: "0"
            })
        }));

        // Get the like button element, and click on it to add the Like.
        const like_btn_qs = "button[data-code='+']";
        const like_btn_el = reactions_panel_el.querySelector(like_btn_qs);
        expect(like_btn_el != undefined);
        fireEvent.click(like_btn_el);

        const formData = new dom.window.FormData();
        formData.append("reaction", "+");
        formData.append("csrfmiddlewaretoken", null);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/react/29/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await waitFor(() => {
            const feedback_qs = '#cm-feedback-29';
            const reaction_qs = '[data-reaction="+"]';

            // The feedback element does exist and has two direct children.
            const feedback_el = comment_el.querySelector(feedback_qs);
            expect(feedback_el !== null);
            expect(feedback_el.children.length === 2);

            // The like reaction element does exist too.
            const like_reaction_el = comment_el.querySelector(reaction_qs);
            expect(like_reaction_el != null);
            expect(like_reaction_el.children[0].textContent === '1');
            expect(like_reaction_el.children[1].textContent === '👍');
        });
        dom.window.fetch.mockClear();

        // --------------------------------------
        // Now test that clicking again on the
        // Like button removes the Like reaction.

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({
                html: "<div class=\"active-reactions\"><div class=\"reaction\" data-reaction=\"+\"></div></div>",
                reply_to: "0"
            })
        }));

        // Click on the Like button.
        expect(like_btn_el != undefined);
        fireEvent.click(like_btn_el);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/react/29/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            }
        );

        await waitFor(() => {
            const feedback_qs = '#cm-feedback-29';
            const reaction_qs = '[data-reaction="+"]';

            // The feedback element does exist and has only one direct child.
            const feedback_el = comment_el.querySelector(feedback_qs);
            expect(feedback_el != null);
            expect(feedback_el.children.length === 1);

            // Every feedback element's text child node is empty. They would
            // contain &nbsp; to add padding when there are reactions. But
            // when the reactions are removed, the plugin shall remove the
            // explicit paddings too.
            for (const child of feedback_el.childNodes) {
                if (child.nodeType === Node.TEXT_NODE) {
                    expect(child.textContent === "");
                }
            }

            // The reaction data-code="+" does not exist.
            const like_reaction_el = comment_el.querySelector(reaction_qs);
            expect(like_reaction_el == null);
        });
        dom.window.fetch.mockClear();
    });
});
