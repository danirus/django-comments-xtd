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
    const cm_reactions_div = document.getElementById(`cm-reactions-${cid}`);
    if (data.counter > 0) {
        const new_list = create_reactions_list(data);
        if (cm_reactions_div === null) {
            const reactions = document.createElement("div");
            reactions.id = `cm-reactions-${cid}`;
            reactions.className = "reactions";
            reactions.appendChild(new_list);
            reactions.insertAdjacentHTML("beforeend", "&nbsp;");
            const cm_footer = document.getElementById(`cm-footer-${cid}`);
            cm_footer.insertBefore(reactions, cm_footer.children[0]);
            reactions.insertAdjacentHTML("afterend", "&nbsp;");
        } else {
            const old_list = cm_reactions_div.querySelector(".active-reactions");
            cm_reactions_div.replaceChild(new_list, old_list);
        }
    } else if (cm_reactions_div) {
        cm_reactions_div.remove();
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

export { init_reactions };
