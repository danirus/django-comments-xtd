import { get_cookie } from "./utils";


export default class ReactionsPanel {
  constructor({ panel_el, is_guest, login_url, react_url } = opts) {
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
    const buttons = this.panel_el.querySelectorAll("button");
    for (const btn of buttons) {
      btn.addEventListener("click", this.on_react_btn_click);
      btn.addEventListener("mouseover", this.on_react_btn_mouseover);
      btn.addEventListener("mouseout", this.on_react_btn_mouseout);
    }
  }

  on_react_btn_click(event) {
    if (this.is_guest) {
      globalThis.location.href = `${this.login_url}?next=${this.next_url}`;
    } else {
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
    }
  }

  async handle_reactions_response(response) {
    const data = await response.json();
    const cm_feedback_qs = `#cm-feedback-${this.comment_id}`;
    const cm_reactions_qs = `#cm-reactions-${this.comment_id}`;
    if (response.status === 200 || response.status === 201) {
      const cm_reactions_el = document.querySelector(cm_reactions_qs);
      if (cm_reactions_el) {  // At least another reaction is displayed.
        if (data.html.length === 0) {  // No more reactions listed.
          cm_reactions_el.remove();
        } else {  // Add the new list of reactions.
          cm_reactions_el.innerHTML = data.html;
        }
      } else {  // Create the <div class="reactions">.
        const cm_feedback_el = document.querySelector(cm_feedback_qs);
        const div_reactions = document.createElement("div");
        div_reactions.classList.add("reactions");
        div_reactions.setAttribute("id", `cm-reactions-${this.comment_id}`);
        cm_feedback_el.insertBefore(div_reactions, cm_feedback_el.firstChild);
        div_reactions.innerHTML = data.html;
      }
    } else if (response.status > 400) {
      alert(
        "Something went wrong and your comment reaction could not " +
        "be processed. Please, reload the page and try again."
      );
    }
  }

  on_react_btn_mouseover(event) {
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

  deactivate_emoji_buttons() {
    const cm_reactions_id = `#cm-reactions-${this.comment_id}`;
    const cm_reactions_el = document.querySelector(cm_reactions_id);
    if (cm_reactions_el == undefined)
      return;

    const active_reactions = cm_reactions_el.querySelector(".active-reactions");
    for (const btn of this.panel_el.querySelectorAll("button[data-code]")) {
      btn.classList.remove("active");
    }
  }

  activate_emoji_buttons() {
    const cm_reactions_id = `#cm-reactions-${this.comment_id}`;
    const cm_reactions_el = document.querySelector(cm_reactions_id);
    if (cm_reactions_el == undefined)
      return;

    const active_reactions = cm_reactions_el.querySelector(".active-reactions");
    const reactions = active_reactions.dataset.djcxUserReactions;
    if (reactions && reactions.length > 0) {
      const reaction_list = reactions.split(",");
      for (const reaction of reaction_list) {
        const qs_btn = `button[data-code="${reaction}"]`;
        const btn = this.panel_el.querySelector(qs_btn);
        if (btn) {
          btn.classList.add("active");
        }
      }
    }
  }

  hide() {
    if (this.panel_el) {
      const left = this.panel_el.dataset.fromLeft;
      const top = this.panel_el.dataset.fromTop;
      const transform_text = `translate3d(${left}px, ${top}px, 0)`;
      this.deactivate_emoji_buttons();

      this.panel_el.style.transform = transform_text;
      this.panel_el.style.opacity = 0;
      this.panel_el.style.display = "none";
      this.panel_el.style.zIndex = 0;
    }
  }

  show(trigger_elem, comment_id) {
    this.comment_id = comment_id;
    this.next_url = trigger_elem.dataset.loginNext || "";
    this.panel_el.style.transform = "none";
    this.set_position(trigger_elem);
    this.activate_emoji_buttons();

    const left = this.panel_el.dataset.left;
    const top = this.panel_el.dataset.top;
    const transform_text = `translate3d(${left}px, ${top}px, 0)`;

    this.panel_el.style.zIndex = 1;
    this.panel_el.style.display = "block";
    this.panel_el.style.transform = transform_text;
    this.panel_el.style.opacity = 1;
  }

  get_absolute_coords(elem) {
    if (!elem) {
      return;
    }

    const box = elem.getBoundingClientRect();
    const page_x = globalThis.pageXOffset;
    const page_y = globalThis.pageYOffset;

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
