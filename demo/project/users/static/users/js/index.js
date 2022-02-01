import EmailForm from "./email_form.js";
import PersonalDataForm from "./pdata_form.js";


let email_form = null;
let pdata_form = null;

window.addEventListener("DOMContentLoaded", (_) => {
    if (document.getElementById("email_form")) {
        email_form = new EmailForm('/user/account/edit/email',
            'email_form', 'email_form_msg');
    }

    if (document.getElementById("pdata_form")) {
        pdata_form = new PersonalDataForm('/user/account/edit/pdata',
            'pdata_form', 'pdata_form_msg');
    }
});

window.submit_email_form = () => email_form ? email_form.post() : false;
window.submit_pdata_form = () => pdata_form ? pdata_form.post() : false;
