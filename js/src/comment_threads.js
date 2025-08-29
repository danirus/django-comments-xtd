/** Comment Threads.
 *
 *  Is in charge of folding and unfolding comments upon click on
 *  comment threads (the blue lines displayes at the left side).
 *
 * |-- c0 (level 0) --
 * |---- c1 (level 1) --
 * |------ c2 (level 2) -- cfold: folded
 * |-------- c3 (level 3, hidden) --
 *
 * If I fold c1, and c2 is already folded.
 */

export default class CommentThreads {
  /* For nested comments, this function adds and removes the class
   * 'active' to comments that belong to the same parent thread.
   * The fold/unfold link receives the 'active' class, as it
   * has the data set attribute `data-djcx-cthread-id` too.
   */

  constructor() {
    this.click_handler = this.click_handler.bind(this);
    this.get_nested_cids = this.get_nested_cids.bind(this);
    this.mouseover_handler = this.mouseover_handler.bind(this);
    this.mouseout_handler = this.mouseout_handler.bind(this);

    for (const elem of document.querySelectorAll(".cthread")) {
      elem.addEventListener("mouseover", this.mouseover_handler);
      elem.addEventListener("mouseout", this.mouseout_handler);
      elem.addEventListener("click", this.click_handler);
    };
    for (const elem of document.querySelectorAll(".cfold")) {
      elem.addEventListener("mouseover", this.mouseover_handler);
      elem.addEventListener("mouseout", this.mouseout_handler);
      elem.addEventListener("click", this.click_handler);
    };
  }

  mouseover_handler(el) {
    const cthread_id = el.target.dataset.djcxCthreadId;
    const qgroup = `[data-djcx-cthread-id='${cthread_id}']`;
    for (const group_el of document.querySelectorAll(qgroup)) {
      group_el.classList.add("active");
    }
  }

  mouseout_handler(el) {
    const cthread_id = el.target.dataset.djcxCthreadId;
    const qgroup = `[data-djcx-cthread-id='${cthread_id}']`;
    for (const group_el of document.querySelectorAll(qgroup)) {
      group_el.classList.remove("active");
    }
  }

  is_visible(comment_el) {
    /* A comment is considered visible if its div comment-box does
     * not have the class 'hide' and its a.cfold does not have
     * the class 'folded'.
     */
    const comment_id = comment_el.dataset.djcxCid;
    const cfold_qs = `a.cfold[data-djcx-cthread-id="${comment_id}"]`;
    const cfold_el = document.querySelector(cfold_qs);
    const folded = cfold_el && cfold_el.classList.contains("folded");
    const is_visible = !comment_el.classList.contains("hide") && !folded;
    return is_visible;
  }

  get_nested_cids(cthread_id) {
    /* Returns the array of comment ids that are nested in the
     * given thread id. It takes care of NOT returning comments
     * that have are already hidden unless the data-djcx-fold
     * corresponds to the thread id being unfolded. That property
     * data-djcx-fold is established at the time the user folds
     * the thread.
     */
    const result = new Set();
    const qs = `[data-djcx-cthread-id="${cthread_id}"]`;
    for (const elem of document.querySelectorAll(qs)) {
      const comment_el = elem.closest("div.comment-box[data-djcx-cid]");
      if (
        comment_el
        && comment_el.dataset.djcxCid != cthread_id     // Exclude itself.
        && (
          !comment_el.classList.contains("hide")        // For folding.
          || comment_el.dataset.djcxFold == cthread_id  // For unfolding.
        )
      ) {
        result.add(comment_el.dataset.djcxCid);
      }
    }
    return result;
  }

  click_handler(el) {
    el.preventDefault();
    const cthread_id = el.target.dataset.djcxCthreadId;

    /* If element with id `comment-${cthread_id}-replies`
     * does not exist, there is no comments thread to fold/unfold.
     */
    const replies_id = `comment-${cthread_id}-replies`;
    if (document.getElementById(replies_id) == undefined) {
      return;
    }

    /* Add or remove class 'folded', and hide or display
     * the list of comments that belong to the clicked thread.
     */
    // Get the Set of the comments nested inside `cthread_id` comment.
    const nested_cids = this.get_nested_cids(cthread_id);
    const anchor_qs = `a.cfold[data-djcx-cthread-id="${cthread_id}"]`;
    const anchor_el = document.querySelector(anchor_qs);
    const threads_qs = `a.cthread[data-djcx-cthread-id="${cthread_id}"]`;

    // Unfold the comments...
    if (anchor_el.classList.contains("folded")) {
      anchor_el.classList.remove("folded");
      for (const thread_el of document.querySelectorAll(threads_qs)) {
        thread_el.classList.remove("folded");
      }
      // Remove the 'hide' class from comment-box and reply-box
      // divs whose data-djcx-cid is in nested_cids.
      for (const comment_id of nested_cids.values()) {
        const div_qs = `div[data-djcx-cid="${comment_id}"]`;
        const div_elems = document.querySelectorAll(div_qs);
        for (const div_el of div_elems) {
          div_el.classList.remove("hide");
        }
      }
    // ... or otherwise fold them.
    } else {
      anchor_el.classList.add("folded");
      for (const thread_el of document.querySelectorAll(threads_qs)) {
        thread_el.classList.add("folded");
      }
      // Add the 'hide' class to comment-box and reply-box divs
      // whose data-djcx-cid is in nested_cids.
      for (const comment_id of nested_cids.values()) {
        const div_qs = `div[data-djcx-cid="${comment_id}"]`;
        const div_elems = document.querySelectorAll(div_qs);
        for (const div_el of div_elems) {
          div_el.classList.add("hide");
          div_el.dataset.djcxFold = cthread_id;
        }
      }

    }
  }
}
