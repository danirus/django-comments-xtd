import { init_comments } from "./comments.js";
import { init_reactions } from "./reactions.js";

window.dcx.init_comments = init_comments;
window.dcx.init_reactions = init_reactions;

window.addEventListener("DOMContentLoaded", (_) => {
    if (window.dcx === null) {
        return;
    }

    init_comments();
    init_reactions();
});
