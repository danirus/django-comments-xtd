import ReactionsPanel from "./reactions_panel";
import { get_login_url, get_react_url } from "./utils";


export default class ReactionHandler {
  constructor(config_el) {
    this.cfg_el = config_el;
    this.is_guest = this.cfg_el.dataset.djcxIsGuestUser === "1";  // If anon.
    this.is_input_allowed = this.cfg_el.dataset.djcxIsInputAllowed === "1";
    this.login_url = get_login_url(this.cfg_el, this.is_guest);
    this.react_url = get_react_url(this.cfg_el, this.is_guest);

    this.hide_panel = this.hide_panel.bind(this);
    this.on_document_click = this.on_document_click.bind(this);
    this.on_document_key_up = this.on_document_key_up.bind(this);

    // Initialize the buttons panels and their components.
    this.links = document.querySelectorAll("[data-djcx=reactions-panel]");
    if (this.links.length === 0 && this.is_input_allowed) {
      throw new Error(
        "Cannot initialize reactions panel => There are " +
        "no elements with [data-djcx=reactions-panel].");
    }
    this.active_visible_panel = 0;
    this.panels_visibility = new Map(); // Keys are 'comment_id'.
    this.event_handlers = [];
    this.add_event_listeners();
    this.listen_to_click_on_links();
    const qs_panel = "[data-djcx=reactions-panel-template]";
    this.panel_el = document.querySelector(qs_panel);
    if (this.panel_el === undefined) {
      throw new Error("Cannot find element with ${qs_panel}.");
    }

    // Create object of class ReactionsPanel in charge of showing and
    // hiding the reactions panel around the clicked 'react' link
    // element.
    this.reactions_panel = new ReactionsPanel({
      panel_el: this.panel_el,
      is_guest: this.is_guest,
      login_url: this.login_url,
      react_url: this.react_url
    });
  }

  hide_panel() {
    if (this.active_visible_panel !== 0) {
      this.reactions_panel.hide();
      this.panels_visibility.set(this.active_visible_panel, false);
      this.active_visible_panel = 0;
    }
  }

  on_document_click(event) {
    const data_attr = event.target.dataset.djcx;
    if (!data_attr || data_attr !== "reactions-panel") {
      this.hide_panel();
    }
  }

  on_document_key_up(event) {
    if (event.key === "Escape") {
      this.hide_panel();
    }
  }

  add_event_listeners() {
    globalThis.document.addEventListener('click', this.on_document_click);
    globalThis.document.addEventListener('keyup', this.on_document_key_up);

    this.event_handlers.push({
      elem: globalThis.document,
      event: 'click',
      handler: this.on_document_click,
    }, {
      elem: globalThis.document,
      event: 'keyup',
      handler: this.on_document_key_up,
    });
  }

  remove_event_listeners() {
    for (const item of this.event_handlers) {
      item.elem.removeEventListener(item.event, item.handler);
    }
  }

  listen_to_click_on_links() {
    for (const elem of this.links) {
      if (elem.dataset.comment === null) {
        continue;
      }
      const comment_id = Number.parseInt(elem.dataset.comment);
      const click_handler = this.toggle_reactions_panel(comment_id);
      elem.addEventListener("click", click_handler);
      this.event_handlers.push({
        'elem': elem,
        'event': 'click',
        'handler': click_handler
      });
      // Not visible yet:
      this.panels_visibility.set(comment_id, false);
    }
  }

  toggle_panel(event, comment_id) {
    const is_visible = this.panels_visibility.get(comment_id);
    if (is_visible) {
      this.active_visible_panel = 0;
      this.reactions_panel.hide();
    } else {
      this.active_visible_panel = comment_id;
      this.reactions_panel.show(event.target, comment_id);
    }
    this.panels_visibility.set(comment_id, !is_visible);
  }

  toggle_reactions_panel(comment_id) {
    return (event) => {
      event.preventDefault();
      const prev_id = this.active_visible_panel;
      if (prev_id !== 0 && prev_id != comment_id) {
        this.active_visible_panel = 0;
        this.reactions_panel.hide();
        this.panels_visibility.set(prev_id, false);
        setTimeout(() => {
          this.toggle_panel(event, comment_id);
        }, 50);
      } else {
        this.toggle_panel(event, comment_id);
      }
    };
  }

}
