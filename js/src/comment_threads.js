/** Comment Threads.
 *
 *  Is in charge of folding and unfolding comments upon click on
 *  comment threads (the blue lines displayes at the left side).
 *
 */
import { digest_loc } from "./utils";


export default class CommentThreads {
  /* For nested comments, this function adds and removes the class
   * 'active' to comments that belong to the same parent thread.
   * The fold/unfold link receives the 'active' class, as it
   * has the data set attribute `data-djcx-cthread-id` too.
   */

  constructor(sst_key) {
    this.click_handler = this.click_handler.bind(this);

    for (const elem of document.querySelectorAll(".vline")) {
      elem.addEventListener("click", this.click_handler);
    };
    for (const elem of document.querySelectorAll(".cfold")) {
      elem.addEventListener("click", this.click_handler);
    };

    this.sst_key = `djcx:${sst_key}:folded`;
    this.folded_cids = new Set();
    const sst_value = globalThis.sessionStorage.getItem(this.sst_key);
    if (sst_value) {
      for (const cid of sst_value.split(",")) {
        this.folded_cids.add(Number.parseInt(cid));
        this.fold_on_startup(cid);
      }
    }
  }

  static async initialize() {
    sst_key = await digest_loc();
    return new CommentThreads(sst_key);
  }

  get_cthread_elements(cthread_id) {
    /*
    * Returns a tuple with two elements. The first is the the HTML
    * element that keeps track of the number of nested comments in
    * a comment. The second represents its vertical line.
    */
    const anchor_qs = `a.cfold[data-djcx-cthread-id="${cthread_id}"]`;
    const vline_qs = `a.vline[data-djcx-cthread-id="${cthread_id}"]`;
    const anchor_el = document.querySelector(anchor_qs);
    const vline_el = document.querySelector(vline_qs);

    return [anchor_el, vline_el];
  }

  fold_on_startup(cthread_id) {
    /* If element with id `comment-${cthread_id}-replies`
     * does not exist, there is no comments thread to fold/unfold.
     */
    const replies_id = `comment-${cthread_id}--replies`;
    if (document.getElementById(replies_id) == undefined) {
      return;
    }
    const [anchor_el, vline_el] = this.get_cthread_elements(cthread_id);
    this.fold_comments(cthread_id, anchor_el, vline_el);
  }

  unfold_comments(cthread_id, anchor_el, vline_el) {
    anchor_el.classList.remove("folded");
    vline_el.classList.remove("folded");

    // The element with class `thread-group` contains:
    //  * the comment with the `cthread_id`,
    //  * its nested comments inside a `cmthread`` div,
    //  * and the `reply-box`.
    const tgroup_qs = `div.thread-group[data-djcx-cthread-id="${cthread_id}"]`;
    const tgroup_el = document.querySelector(tgroup_qs);

    for (const element of tgroup_el.children) {
      if (element.classList.contains("cmthread")) {
        // If the element is the list of children, folded it with
        // everything inside: comment, nested comments, reply-box.
        element.classList.remove("folded");
      }
    }

    this.folded_cids.delete(Number.parseInt(cthread_id));
    globalThis.sessionStorage.setItem(
      this.sst_key,
      Array.from(this.folded_cids).join(",")
    );
  }

  fold_comments(cthread_id, anchor_el, vline_el) {
    anchor_el.classList.add("folded");
    vline_el.classList.add("folded");

    const tgroup_qs = `div.thread-group[data-djcx-cthread-id="${cthread_id}"]`;
    const tgroup_el = document.querySelector(tgroup_qs);

    for (const element of tgroup_el.children) {
      if (element.classList.contains("cmthread")) {
        element.classList.add("folded");
      }
    }

    this.folded_cids.add(Number.parseInt(cthread_id));
    globalThis.sessionStorage.setItem(
      this.sst_key,
      Array.from(this.folded_cids).join(",")
    );
  }

  click_handler(el) {
    el.preventDefault();
    const cthread_id = el.target.dataset.djcxCthreadId;

    /* If element with id `comment-${cthread_id}-replies`
     * does not exist, there is no comments thread to fold/unfold.
     */
    const replies_id = `comment-${cthread_id}--replies`;
    if (document.getElementById(replies_id) == undefined) {
      return;
    }

    /* Otherwise add/remove class 'folded', and hide/display
     * the list of comments that belong to the clicked thread.
     */
    // Get the group of comments nested inside `cthread_id` comment.
    const [anchor_el, vline_el] = this.get_cthread_elements(cthread_id);
    if (anchor_el.classList.contains("folded")) {
      this.unfold_comments(cthread_id, anchor_el, vline_el);
    } else {
      this.fold_comments(cthread_id, anchor_el, vline_el);
    }
  }
}
