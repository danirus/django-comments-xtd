function setLanguage(event) {
    event.preventDefault();
    const link = event.target;
    const form = document.getElementById("langform");
    let fields = {
        csrfmiddlewaretoken: form.elements['csrfmiddlewaretoken'].value,
        language: link.dataset.value,
        next: ""
    }
    let formBody = [];
    for (const field in fields) {
        let key = encodeURIComponent(field);
        let value = encodeURIComponent(fields[field]);
        formBody.push(`${key}=${value}`);
    }
    formBody = formBody.join("&");
    fetch('/i18n/setlang/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset-UTF-8',
      },
      body: formBody
    }).then((data) => {
      if (data.status  == 200) {
        window.location.href = data.url;
      }
    });
}

/* initDropdown signature:
 * initDropdown(elemId, onChange, shallDelegate)
 *  -elemId: id of the element with class="dropdown" containing the <select>.
 *  -onChange: if given, the callback function to call when an option is
 *             selected.
 *  -shallDelegate: boolean, if true the onChange function is called
 *                  immediately. Otherwise it is called after the option
 *                  has been updated in the UI.
 */
initDropdown("language-dropdown", setLanguage, true);