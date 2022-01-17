const avatar_form_id = "avatar_form";

window.addEventListener("DOMContentLoaded", (_) => {
  function getChecked() {
    // Remove "selected" class from all LI.
    const selector = "input[type=radio][name=choice]";
    const radio_list = document.querySelectorAll(selector);
    for (const item of radio_list) {
      item.parentNode.parentNode.classList.remove("selected");
    }
    // Add "selected" to the checked radio button.
    const selected = document.querySelector(`${selector}:checked`);
    selected.parentNode.parentNode.classList.add("selected");
  }

  // Show the selected radio button.
  getChecked();

  // Change the selected on form change.
  document.querySelector(`#${avatar_form_id}`)
    .addEventListener("change", getChecked);
});

// Update the 'choices' field.
// Required to delete avatar.
window.submit_avatar_form = (_) => {
  const form = document.getElementById(`${avatar_form_id}`);
  form.elements['choices'].value = form.elements['choice'].value;
  return true;
}