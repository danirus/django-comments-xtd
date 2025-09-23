/** Comment Threads.
 *
 *  Is in charge of folding and unfolding comments upon click on
 *  comment threads (the blue lines displayes at the left side).
 *
 */

export default class CommentThreads {
  /* For nested comments, this function adds and removes the class
   * 'active' to comments that belong to the same parent thread.
   * The fold/unfold link receives the 'active' class, as it
   * has the data set attribute `data-djcx-cthread-id` too.
   */

  constructor() {
    this.click_handler = this.click_handler.bind(this);

    for (const elem of document.querySelectorAll(".vline")) {
      elem.addEventListener("click", this.click_handler);
    };
    for (const elem of document.querySelectorAll(".cfold")) {
      elem.addEventListener("click", this.click_handler);
    };
  }

  click_handler(el) {
    el.preventDefault();
    const cthread_id = el.target.dataset.djcxCthreadId;
    console.log(`Clicked cthread-id: ${cthread_id}`);

    /* If element with id `comment-${cthread_id}-replies`
     * does not exist, there is no comments thread to fold/unfold.
     */
    const replies_id = `comment-${cthread_id}--replies`;
    if (document.getElementById(replies_id) == undefined) {
      return;
    }

    /* Add or remove class 'folded', and hide or display
     * the list of comments that belong to the clicked thread.
     */
    // Get the Set of the comments nested inside `cthread_id` comment.
    const anchor_qs = `a.cfold[data-djcx-cthread-id="${cthread_id}"]`;
    const vline_qs = `a.vline[data-djcx-cthread-id="${cthread_id}"]`;
    const anchor_el = document.querySelector(anchor_qs);
    const vline_el = document.querySelector(vline_qs);
    const tgroup_qs = `div.thread-group[data-djcx-cthread-id="${cthread_id}"]`;
    const tgroup_el = document.querySelector(tgroup_qs);

    // Unfold the comments...
    if (anchor_el.classList.contains("folded")) {
      anchor_el.classList.remove("folded");
      vline_el.classList.remove("folded");

      // The element with class `thread-group` contains the comment
      // with the `cthread_id`, its nested comments inside a `cmthread``
      // div, and the `reply-box`.
      for (const element of tgroup_el.children) {
        if (element.classList.contains("cmthread")) {
          // If the element is the list of children, folded it with
          // everything inside: comment, nested comments, reply-box.
          element.classList.remove("folded");
        } else if (
          element.dataset
          && element.dataset.djcxCid
          && element.dataset.djcxCid != cthread_id
        ) {
          // I think this never happens, lets log it:
          console.log("I am removing 'folded' from a comment, weird?");
          element.classList.remove("folded");
        }
      }

    // ... or otherwise fold them.
    } else {
      anchor_el.classList.add("folded");
      vline_el.classList.add("folded");

      for (const element of tgroup_el.children) {
        if (element.classList.contains("cmthread")) {
          element.classList.add("folded");
        } else if (
          element.dataset
          && element.dataset.djcxCid
          && element.dataset.djcxCid != cthread_id
        ) {
          // I think this never happens, lets log it:
          console.log("I am adding 'folded' to a comment, weird?");
          comment_el.classList.add("folded");
        }
      }
    }
  }
}
