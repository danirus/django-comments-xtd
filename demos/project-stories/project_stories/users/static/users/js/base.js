export default class BaseForm {
  constructor(url, formId, formMsgId) {
    this.url = url;
    this.form = document.getElementById(formId);
    this.msg = document.getElementById(formMsgId);
  }

  cleanMessage() {
    const classes = [
      'alert-success', 'alert-info', 'alert-warn', 'alert-error',
      'text-success', 'text-info', 'text-warn', 'text-error'
    ];
    this.msg.classList.add("hide");
    this.msg.textContent = "";
    for (let classname of classes) {
      this.msg.classList.remove(classname);
    }
  }

  setMessage(text, remove_classes, add_classes) {
    for(let classname of remove_classes.split(" ")) {
      this.msg.classList.remove(classname);
    }
    for(let classname of add_classes.split(" ")) {
      this.msg.classList.add(classname);
    }
    this.msg.textContent = text;
  }

  post(_) {}
}