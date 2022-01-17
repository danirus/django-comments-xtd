import CommentForm from "./comment_form.js";

export default class ReplyFormsHandler {
  constructor(baseReplyFormId, qsRepliesFormWrapper) {
    this.baseReplyFormEl = document.getElementById(baseReplyFormId);
    this.replyMap = new Map();

    for (let elem of document.querySelectorAll(qsRepliesFormWrapper)) {
      const rFormEl = elem.querySelector("form");
      if (rFormEl == null) continue;

      const rFormWrapperEl = rFormEl.parentNode;
      // const action = rFormEl.action;
      const reply_to = rFormEl.elements['reply_to'].value;
      const qs_cform = `${rFormWrapperEl.dataset.dcx}-${reply_to}`;
      rFormWrapperEl.dataset.dcx = qs_cform;
      console.log(`dataset.dcx: `, rFormWrapperEl.dataset.dcx);


      // The textarea with "Your reply" placeholder.
      const ta = document.createElement("textarea");
      ta.rows = 1;
      ta.placeholder = "Your reply";
      ta.addEventListener("focus", this.on_focus(reply_to));

      // Wrapper for the textarea.
      const replyTADiv = document.createElement("div");
      replyTADiv.setAttribute("data-dcx", "reply-textarea");
      replyTADiv.className = "reply-form";
      replyTADiv.appendChild(ta);

      const newForm = this.baseReplyFormEl.cloneNode(true);
      newForm.id = `${newForm.id}-${reply_to}`;
      newForm.elements['reply_to'].value = reply_to;
      const post_btn = newForm.elements['post'];
      post_btn.addEventListener("click", this.on_post(reply_to));
      const preview_btn = newForm.elements['preview'];
      preview_btn.addEventListener("click", this.on_preview(reply_to));
      const cancel_btn = newForm.elements['cancel'];
      cancel_btn.addEventListener("click", this.on_cancel(reply_to));
      newForm.style.display = "none";

      elem.appendChild(replyTADiv);
      console.log(`newForm:`, newForm);
      rFormEl.replaceWith(newForm);
      this.replyMap.set(reply_to, {
        'node': rFormWrapperEl,
        'cform': new CommentForm(`[data-dcx=${qs_cform}]`)
      });
    }
  }

  on_focus(reply_to) {
    // Display the comment form and hide the text area.
    return (event) => {
      const item = this.replyMap.get(reply_to);
      if (item === undefined) {
        console.error(`Could not find reply holder for comment id ${reply_to}`);
        return;
      }

      const form = item.node.querySelector("form");
      const divta = item.node.querySelector("[data-dcx=reply-textarea]");
      item.node.classList.toggle("active");
      divta.style.display = "none";
      form.style.display = "grid";
      form.elements['comment'].focus();
    }
  }

  on_cancel(reply_to) {
    // Display the text area and hide the comment form.
    return (event) => {
      const item = this.replyMap.get(reply_to);
      if (item === undefined) {
        console.error(`Could not find reply holder for comment id ${reply_to}`);
        return;
      }

      const form = item.node.querySelector("form");
      const divta = item.node.querySelector("[data-dcx=reply-textarea]");
      divta.querySelector("textarea").value = form.elements['comment'].value;
      item.node.classList.toggle("active");
      form.style.display = "none";
      divta.style = "";
    }
  }

  on_preview(reply_to) {
    return (event) => {
      console.log(`Clicked on reply_form with reply_to ${reply_to}`);
      const item = this.replyMap.get(reply_to);
      if (item === undefined) {
        console.error(`Could not find reply holder for comment id ${reply_to}`);
        return;
      }

      const form = item.node.querySelector("form");
      console.log(`form.reply_to:`, form.elements['reply_to'].value);
      item.cform.post("preview");
    }
  }

  on_post(reply_to) {
    return (event) => {
      console.log(`Clicked on reply_form with reply_to ${reply_to}`);
      const item = this.replyMap.get(reply_to);
      if (item === undefined) {
        console.error(`Could not find reply holder for comment id ${reply_to}`);
        return;
      }

      const form = item.node.querySelector("form");
      console.log(`form.reply_to:`, form.elements['reply_to'].value);
      item.cform.post("post");
    }
  }
}
