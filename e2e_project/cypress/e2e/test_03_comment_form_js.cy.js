describe('Test /03-logout-and-def-dark--comment-form-js', () => {
  const comment = (
    "This comment form is sent in preview directly in the "
    + "template `form_js_test.html`, and rendered with the JS plugin."
  );
  const name = "Joe Bloggs";
  const email = "joe@example.com";

  beforeEach(() => {
    cy.visit("/03-logout-and-def-dark--comment-form-js");
  });

  it("contains two sections", () => {
    // The div[data-djcx='comment-form'] has two sections:
    // * one with the preview of the comment, and
    // * another with the comment form.

    // Check that the first section is the one with the comment preview.
    cy.get("[data-djcx='comment-form'] section:first-child")
      .should("have.class", "comment-preview", "mb32")
      .should("have.data", "djcx");

    // Check that the last section is the one with the comment form.
    cy.get("[data-djcx='comment-form'] section:last-child")
      .should("have.class", "comment-form");
  });

  it("displays the preview in the first-child section", () => {
    cy.get("[data-djcx='preview'] div")
      .should("have.class", "comment-box", "l1");

    cy.get("[data-djcx='preview'] div.comment-box div.comment")
      .get("div.header > div:first-child")
      .should("have.text", name);

    cy.get("[data-djcx='preview'] div.comment-box div.comment")
      .get("div.header > div:last-child")
      .should("have.class", "small", "text-info")
      .should("have.text", "comment in preview");

    cy.get("[data-djcx='preview'] div.comment-box div.comment")
      .get("div.body")
      .should("have.class", "body-bordered body-bordered--no-bottom")
      .should("contain", comment);

    cy.get("[data-djcx='preview'] div.comment-box div.comment")
      .get("div.feedback")
      .should("have.class", "feedback-bordered")
      .should("have.text", "");
  });

  it("displays the comment-form in the last-child section", () => {
    cy.get("[data-djcx='comment-form'] section:last-child")
      .should("have.class", "comment-form");

    // The header: "Post your comment".
    cy.get("[data-djcx='comment-form'] section:last-child")
      .get("h5")
      .should("have.class", "text-center")
      .should("contain", "Post your comment");

    // The form.
    cy.get("[data-djcx='comment-form'] section:last-child")
      .get("form")
      .should("have.attr", "method", "POST")
      .should("have.attr", "autocomplete", "off")
      .should("have.attr", "action", "/comments/post/");
  });

  it("displays the 'comment' textarea field in the form", () => {
    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("textarea[name='comment']")
      .should("have.attr", "placeholder", "Your comment")
      .should("have.attr", "required", "required")
      .should("have.value", comment);
  });

  it("displays the 'name' label and field in the form", () => {
    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("label[for='id_name']")
      .should("have.class", "col1");

    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("input[name='name']")
      .should("have.attr", "placeholder", "name")
      .should("have.attr", "required", "required")
      .should("have.attr", "id", "id_name")
      .should("have.attr", "type", "text")
      .should("have.value", name);
  });

  it("displays the 'email' label and field in the form", () => {
    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("label[for='id_email']")
      .should("have.class", "col1");

    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("input[name='email']")
      .should("have.attr", "aria-describedby", "id_email_helptext")
      .should("have.attr", "placeholder", "mail address")
      .should("have.attr", "required", "required")
      .should("have.attr", "id", "id_email")
      .should("have.attr", "type", "text")
      .should("have.value", email);
  });

  it("displays the 'follow-up' label and field in the form", () => {
    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("input[name='followup']")
      .should("have.attr", "type", "checkbox");

    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get(":checkbox:not(:checked)")
      .should("have.length", 1);

    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("label[for='id_followup']")
      .should("contain", "Notify me about follow-up comments");
  });

  it("displays 'send' and 'preview' buttons in the form", () => {
    // Button SEND.
    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("div.col2")
      .should('have.length', 6)
      .eq(5)  // div.col2 in position 5 of the array.
      .get("button[type='button']")
      .should('have.length', 2)
      .eq(0)  // button position 0 of the array.
      .should("have.class", "primary")
      .should("have.attr", "name", "post")
      .should("have.attr", "value", "1");

    // Button PREVIEW.
    cy.get("[data-djcx='comment-form'] section:last-child form")
      .get("div.col2")
      .should('have.length', 6)
      .eq(5)  // div.col2 in position 5 of the array.
      .get("button[type='button']")
      .should('have.length', 2)
      .eq(1)  // button position 1 of the array.
      .should("have.class", "secondary")
      .should("have.attr", "name", "preview")
      .should("have.attr", "value", "1");
  });
});
