import VoteHandler from "./vote_handler";

function init_voting(cfg) {
  // Handler for clicking events on vote up/down elements.
  globalThis.djcx.vote_handler = undefined;

  /* ----------------------------------------------
   * Initialize voting up/down of comments with level == 0.
   */
  if (globalThis.djcx.vote_handler === undefined) {
    globalThis.djcx.vote_handler = new VoteHandler(cfg);
  }
}

export { init_voting }