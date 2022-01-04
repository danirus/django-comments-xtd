export default class ReplyFormsHandler {
  constructor(qsCommentFormWrapper, qsRepliesFormWrapper) {
    const cFormWrapperEl = document.querySelector(qsCommentFormWrapper);
    this.cFormEl = cFormWrapperEl.querySelector("form");
    this.replyData = [];

    for (let elem of document.querySelectorAll(qsRepliesFormWrapper)) {
      const rFormEl = elem.querySelector("form");
      if (rFormEl == null) continue;

      const rFormWrapperEl = rFormEl.parentNode;
      const action = rFormEl.action;
      const reply_to = rFormEl.elements['reply_to'].value;

      // The textarea with "Your reply" placeholder.
      const ta = document.createElement("textarea");
      ta.rows = 1;
      ta.placeholder = "Your reply";
      ta.addEventListener("focus", this.on_focus(reply_to));
      ta.addEventListener("blur", this.on_blur(reply_to));

      // Wrapper for the textarea.
      const replyTADiv = document.createElement("div");
      replyTADiv.setAttribute("data-dcx", "reply-textarea");
      replyTADiv.className = "reply-form";
      replyTADiv.appendChild(ta);

      // Find visible element where to append the replyTADiv.
      // const repBtnDiv = rFormEl.querySelector("[data-dcx=reply-button]");
      // repBtnDiv.style.display = "none";

      // Append replyTADiv to the parent node of the repBtnDiv.
      // repBtnDiv.parentNode.appendChild(replyTADiv);

      const newForm = this.cFormEl.cloneNode(true);
      newForm.action = action;
      newForm.elements['reply_to'].value = rFormEl.elements['reply_to'].value;
      newForm.style.display = "none";

      // Add 'cancel' button to the newForm.
      const cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      const newFormButtons = newForm.querySelectorAll("button");
      newFormButtons.forEach(item => item.classList.add("small"));
      const lastBtn = newFormButtons[newFormButtons.length - 1];
      cancelBtn.className = lastBtn.className;
      newFormButtons[0].parentNode.appendChild(cancelBtn);

      // This is to attach to JavaScript, it's better to produce the form
      // with a django template tag, so that the user can customize it.
      // And then clone it here, instead of cloning the form.html.
      // Use the tag as: {% render_comment_reply_form for object %}.

      elem.appendChild(replyTADiv);
      rFormEl.replaceWith(newForm);

      const item = {
        reply_holder: rFormWrapperEl,
        action: action,
        reply_to: rFormEl.elements['reply_to'].value,
        reply_textarea: replyTADiv,
        new_form: newForm
      }
      this.replyData.push(item);
    }
    console.log(`replyData:`, this.replyData);
  }

  on_focus(reply_to) {
    return (event) => {
      const section = event.target.parentNode.parentNode;
      if (section == null) {
        console.error("Could not find the element with [data-dcx=reply-form].");
        return;
      }
      event.target.parentNode.style.display = "none";
      section.classList.toggle("active");
      section.children[0].style.display = "grid";
      // event.target.parentNode.className = "reply-form active";
      console.log(`Form for reply_to ${reply_to} got on focus.`);
    }
  }

  on_blur(reply_to) {
    return (event) => {
      event.target.parentNode.className = "reply-form";
      console.log(`Textarea for reply_to ${reply_to} lost the focus.`);
    }
  }
}
