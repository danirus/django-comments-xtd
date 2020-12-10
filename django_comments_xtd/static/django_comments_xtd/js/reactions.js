let reaction_choices = [];
let reactions_url = "/comments/api/react/";
let row_length = 4;
let header_title = "Pick your reaction";

function _init_reaction_choices(elem) {
  const reactions = elem.getAttribute("data-reactions");
  if (reactions == null) {
    throw new Error("Cannot initialize reactions panel => Element with " +
                    "[data-type=reactions-def] attribute is missing " +
                    "[data-reactions] attribute.");
  } else if (reactions.length == 0) {
    throw new Error("Cannot initialize reactions panel => The " +
                    "[data-reactions] attribute is empty.");
  }
  const choices = reactions.split(";");
  if (choices.length < 2) {
    throw new Error("Cannot initialize reactions panels => The " +
                    "[data-reactions] attribute must be a semicolon-" +
                    "separated list of reactions.");
  } else {
    // Check that each choice is a comma-separated list of 3 items.
    for (let i = 0; i < choices.length; i++) {
      if (choices[i].split(",").length != 3) {
        throw new Error("Cannot initialize reactions panels => The " +
                        "[data-reactions] attribute must be a semicolon-" +
                        "separated list of reactions with the format: " +
                        "code,reaction_title,emoji_unicode.");
      }
    }
  }

  return choices;
}

function _init_row_length(elem) {
  try {
    const data_row_length = elem.getAttribute("data-reactions-row-length");
    if (data_row_length == null) {
      throw new Error("Cannot initialize reactions panel => Element with " +
                      "[data-type=reactions-def] attribute is missing " +
                      "[data-reactions-row-length] attribute.");
    }
    return parseInt(data_row_length);
  } catch(e) {
    throw new Error("Cannot initialize reactions panel => The " +
                      "[data-reactions-row-length] attribute must be " +
                      "an integer.");
  }
}

function _init_reactions_url(elem) {
  const url = elem.getAttribute("data-reactions-url");
  if (url == null || url.length == 0) {
    throw new Error("Cannot initialize reactions panel => The " +
    "[data-reactions-url] attribute does not exist or is empty.");
  }
  return url;
}

function init() {
  const rroot = document.querySelector("[data-type=reactions-def]");
  if (rroot == null)
    return;

  /* ----------------------------------------------
   * Initialize global module fields.
   */
  reaction_choices = _init_reaction_choices(rroot);
  row_length = _init_row_length(rroot);
  reactions_url = _init_reactions_url(rroot);
  header_title = rroot.getAttribute("data-reactions-header-title");

  /* ----------------------------------------------
   * Initialize the buttons panels and their components.
   */
  const links = document.querySelectorAll("[data-type=reactions-panel]");
  if (links.length == 0) {
    throw new Error("Cannot initialize reactions panel => There are no " +
                    "elements with [data-type=reactions-panel].");
  }
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

function toggle_buttons_panel(comment_id) {
  return (event) => {
    event.preventDefault();
    // Hide all the panels but the target.
    document.querySelectorAll(".reactions-panel").forEach(elem => {
      if (elem.getAttribute("data-crpanel") != comment_id)
        elem.style.display = "none";
    });
    // Toggle the panel corresponding to the clicked link.
    const panel = document.querySelector(`[data-crpanel="${comment_id}"]`);
    if (panel)
      if(panel.style.display != "block")
        panel.style.display = "block";
      else panel.style.display = "";
  }
}

function create_buttons_panels(nodes) {
  for (let elem of Array.from(nodes)) {
    const anchor_pos = elem.getBoundingClientRect();
    const footer_pos = elem.parentNode.getBoundingClientRect();
    const comment_id = elem.getAttribute("data-comment");
    if (comment_id != null) {
      const panel = document.createElement("div");
      panel.style.bottom = "35px";
      panel.style.left = `${anchor_pos.x - footer_pos.x -10}px`;
      panel.className = "reactions-panel";
      panel.setAttribute("data-crpanel", `${comment_id}`);

      const arrow = document.createElement("div");
      arrow.className = "arrow";
      arrow.style.left = "10px";
      panel.appendChild(arrow);

      const header = document.createElement("h3");
      header.textContent = header_title;
      panel.appendChild(header);

      // For each reaction choice create a reaction button.
      const body = document.createElement("p");
      for (let i=0; i<reaction_choices.length; i++) {
        if (i > 0 && i % row_length == 0)
          body.appendChild(document.createElement("br"));
        const btn = create_reaction_btn(reaction_choices[i], comment_id);
        btn.addEventListener("mouseover", on_mouseover_reaction_btn(header));
        btn.addEventListener("mouseout", on_mouseout_reaction_btn(header));
        body.appendChild(btn);
      }
      panel.appendChild(body);
      elem.parentNode.insertBefore(panel, elem);
      elem.addEventListener("click", toggle_buttons_panel(comment_id));
    }
  }
};

function on_mouseover_reaction_btn(header) {
  return (event) => {
    header.textContent = event.target.getAttribute("data-title");
  }
}

function on_mouseout_reaction_btn(header) {
  return (_) => header.textContent = header_title;
}

function on_click_reaction_btn(crid, cid) {
  return (event) => {
    event.preventDefault();
    console.log(`Clicked on reaction ${crid} on comment ${cid}`);
    post_reaction({ comment: cid, reaction: crid }).then(data => {
      handle_reaction_response(cid, data);
    });
  }
}

function on_mouseover_tooltip(event) {
  const parent_all = event.target.parentNode.parentNode;
  const tooltip = event.target.parentNode.children[0];
  const target_pos = event.target.getBoundingClientRect();
  const parent_all_pos = parent_all.getBoundingClientRect();
  if (tooltip.className == "reactions-tooltip") {
    tooltip.style.display = "block";
    tooltip.style.left = `${-90 + target_pos.x - parent_all_pos.x}px`;
  }
}

function on_mouseout_tooltip(event) {
  const tooltip = event.target.parentNode.children[0];
  if (tooltip.className == "reactions-tooltip")
    tooltip.style.display = "";
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
  const response = await fetch(reactions_url, {
    method: "POST",
    // mode: "no-cors",  // mode "no-cors" makes the post fail.
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

function create_reaction_btn(reaction, cid) {
  const [crid, title, emoji] = reaction.split(",");
  const button = document.createElement("button");
  button.setAttribute("data-title", title);
  button.setAttribute("data-code", crid);
  button.className = "emoji";
  button.innerHTML = `&${emoji};`;
  button.addEventListener("click", on_click_reaction_btn(crid, cid));
  return button;
}

function handle_reaction_response(cid, data) {
  console.log(`handleReactionResponse for comment id`, cid);
  console.log(`response data:`, data);
  const cm_reactions_div = document.getElementById(`cm-reactions-${cid}`);
  if(data.counter > 0) {
    const new_list = create_reactions_list(data);
    if (cm_reactions_div == null) {
      const reactions = document.createElement("div");
      reactions.id = `cm-reactions-${cid}`;
      reactions.className = "reactions";
      reactions.appendChild(new_list);
      reactions.insertAdjacentHTML("beforeend", "&nbsp;");
      const divider = document.createElement("span");
      divider.className = "text-muted";
      divider.innerHTML = "&bull;"
      reactions.appendChild(divider);
      reactions.insertAdjacentHTML("beforeend", "&nbsp;");
      const cm_footer = document.getElementById(`cm-footer-${cid}`);
      cm_footer.insertBefore(reactions, cm_footer.children[0]);
    } else {
      const old_list = cm_reactions_div.querySelector(".active-reactions");
      cm_reactions_div.replaceChild(new_list, old_list);
    }
  } else if (cm_reactions_div)
      cm_reactions_div.remove();
}

function create_reactions_list(data) {
  const list = document.createElement("div");
  list.className = "active-reactions";
  for (let item of data.list) {
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
  let type = event.target.getAttribute("data-type");
  if (type != "reactions-panel") {
    // Clicking outside the "React" link must close the reactions panel.
    document.querySelectorAll(".reactions-panel").forEach(elem => {
      elem.style.display = "none";
    });
  }
});

window.addEventListener("keyup", (event) => {
  if (event.key == "Escape") {
    document.querySelectorAll(".reactions-panel").forEach(elem => {
      elem.style.display = "none";
    });
  }
});

window.addEventListener("load", (_) => init());

export default init;
