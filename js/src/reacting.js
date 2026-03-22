import ReactionHandler from "./reaction_handler.js";

function init_reacting(cfg) {
  globalThis.djcx.reaction_handler = undefined;

  /* ----------------------------------------------
   * Initialize reactions_handler, in charge
   * of all reactions popover components.
   */
  if (
    globalThis.djcx.reaction_handler === undefined
    &&  // and it has comments that can receive reactions:
    cfg.querySelectorAll("div").length > 0
  ) {
    globalThis.djcx.reaction_handler = new ReactionHandler(cfg);
    window.addEventListener("beforeunload", (_) => {
      globalThis.djcx.reaction_handler.remove_event_listeners();
    });
  }
}

export { init_reacting }
