import ReactionsHandler from "./reactions_handler";

function init_reactions() {
    if (window.dcx === null) {
        return;
    }

    const rroot = document.querySelector("[data-dcx=config]");
    if (rroot === null || window.dcx === null) {
        return;
    }

    window.dcx.reactions_handler = null;

    /* ----------------------------------------------
     * Initialize reactions_handler, in charge
     * of all reactions popover components.
     */
    if (window.dcx.reactions_handler === null) {
        window.dcx.reactions_handler = new ReactionsHandler(rroot);
        window.addEventListener("beforeunload", (_) => {
            console.log(`About to call reactions_handler.remove_events()`);
            window.dcx.reactions_handler.remove_event_listeners();
        });

    }
}

export { init_reactions };
