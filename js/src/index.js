import { init_commenting } from "./commenting";
import { init_flagging } from "./flagging";
import { init_reacting } from "./reacting";
import { init_voting } from "./voting";

globalThis.djcx = {
  init_commenting: init_commenting,
  init_flagging: init_flagging,
  init_reacting: init_reacting,
  init_voting: init_voting,
};

globalThis.addEventListener("DOMContentLoaded", (_) => {
  const cfg = document.querySelector("[data-djcx=config]");

  if (cfg) {
    init_commenting(cfg);

    if (cfg.dataset.djcxFlaggingEnabled === "1") {
      init_flagging(cfg);
    }

    if (cfg.dataset.djcxReactingEnabled === "1") {
      init_reacting(cfg);
    }

    if (cfg.dataset.djcxVotingEnabled === "1") {
      init_voting(cfg);
    }

    const djcx_loaded_event = new Event("DjcxLoaded");
    cfg.dispatchEvent(djcx_loaded_event);
  }
});
