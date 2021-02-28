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
   * Initialize the panels and their components.
   */
  const links = document.querySelectorAll("[data-type=reactions-panel]");
  if (links.length == 0) {
    throw new Error("Cannot initialize reactions panel => There are no " +
                    "elements with [data-type=reactions-panel].");
  }
  createPanels(links);
}

function toggleReactionsPanel(comment_id) {
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

function createPanels(nodes) {
  for (let elem of Array.from(nodes)) {
    const comment_id = elem.getAttribute("data-comment");
    if (comment_id != null) {
      const panel = document.createElement("div");
      panel.style.bottom = "35px";
      panel.style.left = "-10px";
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
        const btn = createReaction(reaction_choices[i], comment_id);
        btn.addEventListener("mouseover", handleMouseOverReaction(header));
        btn.addEventListener("mouseout", handleMouseOutReaction(header));
        body.appendChild(btn);
      }
      panel.appendChild(body);
      elem.parentNode.insertBefore(panel, elem);
      elem.addEventListener("click", toggleReactionsPanel(comment_id));
    }
  }
};

function handleMouseOverReaction(header) {
  return (event) => {
    header.textContent = event.target.getAttribute("data-title");
  }
}

function handleMouseOutReaction(header) {
  return (_) => header.textContent = header_title;
}

function handleClickOnReaction(crid, cid) {
  return (event) => {
    event.preventDefault();
    console.log(`Clicked on reaction ${crid} on comment ${cid}`);
    postReaction({ comment: cid, reaction: crid }).then(data => {
      console.log(`response data:`, data);
    });
  }
}

function getCookie(name) {
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

async function postReaction(data) {
  const response = await fetch(reactions_url, {
    method: "POST",
    mode: "no-cors",
    cache: "no-cache",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    redirect: "follow",
    referrerPolicy: "no-referrer",
    body: JSON.stringify(data)
  });
  return response.json();
}

function createReaction(reaction, cid) {
  const [crid, title, emoji] = reaction.split(",");
  const button = document.createElement("button");
  button.setAttribute("data-title", title);
  button.setAttribute("data-code", crid);
  button.className = "emoji";
  button.innerHTML = `&${emoji};`;
  button.addEventListener("click", handleClickOnReaction(crid, cid));
  return button;
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