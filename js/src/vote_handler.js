import { get_cookie, get_login_url, get_vote_url } from "./utils";


export default class VoteHandler {
  constructor(config_el) {
    this.cfg_el = config_el;

    this.is_guest = this.cfg_el.dataset.djcxIsGuestUser === "1";
    this.login_url = get_login_url(this.cfg_el, this.is_guest);
    this.vote_url = get_vote_url(this.cfg_el, this.is_guest);

    this.qs_up = '[data-djcx-action="vote-up"]';
    this.qs_down = '[data-djcx-action="vote-down"]';
    this.on_click = this.on_click.bind(this);

    for(const el of document.querySelectorAll(this.qs_up)) {
      el.addEventListener("click", this.on_click)
    }

    for(const el of document.querySelectorAll(this.qs_down)) {
      el.addEventListener("click", this.on_click)
    }

    /* If the conditions here below are true, the default action that
     * runs on the `commentvote` event is to reload the page... It
     * could better though.
     */
    if (
      ( // Check HTML arguments of element with data-djcx="config".
        !this.cfg_el.dataset.djcxUseDefaultVoteHandler
        || this.cfg_el.dataset.djcxUseDefaultVoteHandler !== "false"
      ) && ( // Additionally check whether JS variable djcx_options.
        !globalThis.djcx_options
        || globalThis.djcx_options.useDefaultVoteHandler !== false
      )
    ) {
      const comments = document.querySelectorAll(".comment-box");
      for(const comment of comments) {
        comment.addEventListener("commentvote", (e) => {
          globalThis.location = e.target.querySelector(".permalink").href;
        });
      }
    }
  }

  on_click(event) {
    event.preventDefault();
    const target = event.target;
    if (this.is_guest) {
      const next_url = target.dataset.loginNext;
      globalThis.location.href = `${this.login_url}?next=${next_url}`;
    } else {
      this.comment_id = target.dataset.comment;
      const vote_url = this.vote_url.replace("0", this.comment_id);
      const code = target.dataset.code;
      const form_data = new FormData();
      form_data.append("vote", code);
      form_data.append("csrfmiddlewaretoken", get_cookie("csrftoken"));

      fetch(vote_url, {
        method: "POST",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        body: form_data
      }).then(response => this.handle_vote_response(response));
    }
  }

  async handle_vote_response(response) {
    const data = await response.json();
    if (response.status === 200 || response.status === 201) {
      const cm_votes_qs = `#cm-votes-${this.comment_id}`;
      const cm_votes_el = document.querySelector(cm_votes_qs);
      if (cm_votes_el) {
        cm_votes_el.innerHTML = data.html;
        const qs_vote_up = cm_votes_el.querySelector(this.qs_up);
        if (qs_vote_up) {
          qs_vote_up.addEventListener("click", this.on_click);
        }
        const qs_vote_down = cm_votes_el.querySelector(this.qs_down);
        if (qs_vote_down) {
          qs_vote_down.addEventListener("click", this.on_click);
        }
        // Dispatch 'commentvote'  event.
        cm_votes_el.closest(".comment-box").dispatchEvent(
          new CustomEvent(
            "commentvote", {
              detail: {
                "comment_id": this.comment_id,
              }
            }
          )
        )
      }
    } else if (response.status > 400) {
      alert(
        "Something went wrong and your comment vote could not " +
        "be processed. Please, reload the page and try again."
      );
    }
  }
}
