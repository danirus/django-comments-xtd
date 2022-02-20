import path from 'path';

import {
    // findByText,
    fireEvent, waitFor,
    // getByLabelText,
    // getByPlaceholderText,
    // getByRole,
    // waitFor
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
        const panel_qs = '[data-crpanel="29"]';
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el !== null);

        const reactions_panel_el = comment_el.querySelector(panel_qs);
        expect(reactions_panel_el !== null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el !== null);

        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            expect(reactions_panel_el.style.display === "block");
        });

        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            expect(reactions_panel_el.style.display === "");
        });
    });

    it("clicks on the 'Like' and displays the 'Like'", async () => {
        const panel_qs = '[data-crpanel="29"]';
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el !== null);

        const reactions_panel_el = comment_el.querySelector(panel_qs);
        expect(reactions_panel_el !== null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el !== null);

        // Click on the 'react' link to open the reactions panel.
        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            expect(reactions_panel_el.style.display === "block");
        });

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({
                counter: 1,
                list: [{
                    'value': '+',
                    'authors': ['Alice Bloggs'],
                    'counter': 1,
                    'label': 'Like',
                    'icon': '#128077'
                }]
            })
        }));

        // Get the like button element, and click on it.
        const like_btn_qs = "button[data-code='+']";
        const like_btn_el = reactions_panel_el.querySelector(like_btn_qs);
        expect(like_btn_el !== undefined);
        fireEvent.click(like_btn_el);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/api/react/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": null,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                redirect: "follow",
                referrerPolicy: "no-referrer",
                body: JSON.stringify({comment: "29", reaction: '+'})
            }
        );

        await waitFor(() => {
            const footer_qs = '#cm-footer-29';
            const reaction_qs = '[data-reaction="+"]';

            // The footer does exist and has two direct children.
            const footer_el = comment_el.querySelector(footer_qs);
            expect(footer_el !== null);
            expect(footer_el.children.length === 2);

            // The like reaction element does exist too.
            const like_reaction_el = comment_el.querySelector(reaction_qs);
            expect(like_reaction_el !== null);

            const tooltip_qs = 'A[data-toggle="reactions-tooltip"]';
            const tooltip_el = like_reaction_el.querySelector(tooltip_qs);
            expect(tooltip_el.textContent === '1👍');
        });

        dom.window.fetch.mockClear();
    });

    it("clicks on the 'Like' to add and remove the 'Like'", async () => {
        const panel_qs = '[data-crpanel="29"]';
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el !== null);

        const reactions_panel_el = comment_el.querySelector(panel_qs);
        expect(reactions_panel_el !== null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el !== null);

        // Click on the 'react' link to open the reactions panel.
        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            expect(reactions_panel_el.style.display === "block");
        });

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({
                counter: 1,
                list: [{
                    'value': '+',
                    'authors': ['Alice Bloggs'],
                    'counter': 1,
                    'label': 'Like',
                    'icon': '#128077'
                }]
            })
        }));

        // Get the like button element, and click on it to add the Like.
        const like_btn_qs = "button[data-code='+']";
        const like_btn_el = reactions_panel_el.querySelector(like_btn_qs);
        expect(like_btn_el !== undefined);
        fireEvent.click(like_btn_el);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/api/react/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": null,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                redirect: "follow",
                referrerPolicy: "no-referrer",
                body: JSON.stringify({comment: "29", reaction: '+'})
            }
        );

        await waitFor(() => {
            const footer_qs = '#cm-footer-29';
            const reaction_qs = '[data-reaction="+"]';

            // The footer does exist and has two direct children.
            const footer_el = comment_el.querySelector(footer_qs);
            expect(footer_el !== null);
            expect(footer_el.children.length === 2);

            // The like reaction element does exist too.
            const like_reaction_el = comment_el.querySelector(reaction_qs);
            expect(like_reaction_el !== null);

            const tooltip_qs = 'A[data-toggle="reactions-tooltip"]';
            const tooltip_el = like_reaction_el.querySelector(tooltip_qs);
            expect(tooltip_el.textContent === '1👍');
        });
        dom.window.fetch.mockClear();

        // --------------------------------------
        // Now test that clicking again on the
        // Like button removes the Like reaction.

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({ counter: 0, list: [] })
        }));

        // Click on the Like button.
        expect(like_btn_el !== undefined);
        fireEvent.click(like_btn_el);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/api/react/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": null,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                redirect: "follow",
                referrerPolicy: "no-referrer",
                body: JSON.stringify({comment: "29", reaction: '+'})
            }
        );

        await waitFor(() => {
            const footer_qs = '#cm-footer-29';
            const reaction_qs = '[data-reaction="+"]';

            // The footer does exist and has only one direct child.
            const footer_el = comment_el.querySelector(footer_qs);
            expect(footer_el !== null);
            expect(footer_el.children.length === 1);

            // Every footer's text child node is empty. They would contain
            // &nbsp; to add padding when there are reactions. But when the
            // reactions are removed, the plugin shall remove the explicit
            // paddings too.
            for (const child of footer_el.childNodes) {
                if (child.nodeType === Node.TEXT_NODE) {
                    expect(child.textContent === "");
                }
            }

            // But the reaction does not.
            const like_reaction_el = comment_el.querySelector(reaction_qs);
            expect(like_reaction_el === null);
        });
        dom.window.fetch.mockClear();
    });

    it("clicks and hovers on the 'Like' to see the tooltip", async () => {
        const panel_qs = '[data-crpanel="29"]';
        const anchor_qs = "A[data-dcx=reactions-panel]";

        const comment_el = container.querySelector("#comment-29");
        expect(comment_el !== null);

        const reactions_panel_el = comment_el.querySelector(panel_qs);
        expect(reactions_panel_el !== null);

        const react_anchor_el = comment_el.querySelector(anchor_qs);
        expect(react_anchor_el !== null);

        // Click on the 'react' link to open the reactions panel.
        fireEvent.click(react_anchor_el);
        await waitFor(() => {
            expect(reactions_panel_el.style.display === "block");
        });

        dom.window.fetch = jest.fn(() => Promise.resolve({
            status: 201,
            json: () => Promise.resolve({
                counter: 1,
                list: [{
                    'value': '+',
                    'authors': ['Alice Bloggs'],
                    'counter': 1,
                    'label': 'Like',
                    'icon': '#128077'
                }]
            })
        }));

        // Get the like button element, and click on it.
        const like_btn_qs = "button[data-code='+']";
        const like_btn_el = reactions_panel_el.querySelector(like_btn_qs);
        expect(like_btn_el !== undefined);
        fireEvent.click(like_btn_el);

        expect(dom.window.fetch.mock.calls.length).toEqual(1);
        expect(dom.window.fetch).toHaveBeenCalledWith(
            "/comments/api/react/",
            {
                method: "POST",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": null,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                redirect: "follow",
                referrerPolicy: "no-referrer",
                body: JSON.stringify({comment: "29", reaction: '+'})
            }
        );

        const reaction_qs = '[data-reaction="+"]';
        let reaction_el = null;

        const tooltip_anchor_qs = 'A[data-toggle="reactions-tooltip"]';
        let tooltip_anchor_el = null;

        await waitFor(() => {
            const footer_qs = '#cm-footer-29';

            // The footer does exist and has two direct children.
            const footer_el = comment_el.querySelector(footer_qs);
            expect(footer_el !== null);
            expect(footer_el.children.length === 2);

            // The like reaction element does exist too.
            reaction_el = comment_el.querySelector(reaction_qs);
            expect(reaction_el !== null);

            tooltip_anchor_el = reaction_el.querySelector(tooltip_anchor_qs);
            expect(tooltip_anchor_el.textContent === '1👍');
        });

        // Set 'mouseover' over the tooltip anchor, so that
        // the tooltip is displayed.
        fireEvent.mouseOver(tooltip_anchor_el);

        await waitFor(() => {
            // The tooltip is the first div within the reaction_el
            // that has a class "reactions-tooltip". Check
            // whether it has a style with 'display: block'.
            const tooltip_el = reaction_el.children[0];
            expect(tooltip_el.classList[0] === 'reactions-tooltip');
            expect(tooltip_el.style.display === 'block');
        });

        // Send event 'mouseout' to the tooltip anchor, so that
        // the tooltip is hidden.
        fireEvent.mouseOut(tooltip_anchor_el);

        await waitFor(() => {
            const tooltip_el = reaction_el.children[0];
            expect(tooltip_el.classList[0] === 'reactions-tooltip');
            expect(tooltip_el.style.display === '');  // defaults to 'none';
        });

        dom.window.fetch.mockClear();
    });
});
