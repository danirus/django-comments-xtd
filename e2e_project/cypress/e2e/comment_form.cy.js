describe('Check form status', () => {
  beforeEach(() => {
    cy.visit("/def-dark--comment-form");
  });

  it("is an invalid form due to missing required fields", () => {
    // The form is invalid due to its input fields.
    // We can call the native HTML method.
    cy.get(".comment-form form").then(
      ($form) => expect($form[0].checkValidity()).to.be.false
    );

    // The three required input fields are invalid at the start.
    cy.get(".comment-form form :invalid").should('have.length', 3);

    // Field with name='comment' is invalid.
    cy.get(".comment-form form [name='comment']:invalid")
      .invoke("prop", "validationMessage")
      .should("equal", "Please fill in this field.");

    // Field with name='name' is invalid.
    cy.get(".comment-form form [name='name']:invalid")
      .invoke("prop", "validationMessage")
      .should("equal", "Please fill in this field.");

    // Field with name='email' is invalid.
    cy.get(".comment-form form [name='email']:invalid")
      .invoke("prop", "validationMessage")
      .should("equal", "Please fill in this field.");
  });
});

describe("Fill the form and send it to the Django backend", () => {
  beforeEach(() => {
    cy.visit("/def-dark--comment-form");
    // Type content for the required fields.
    cy.get("form [name='comment']").type("Your story is inspiring.");
    cy.get("form [name='name']").type("Fulanita de Tal");
    cy.get("form [name='email']").type("fulanita@example.com");
  });

  it("is a valid form when all required fields are filled", () => {
    // The three required input fields are now valid.
    cy.get(".comment-form form :invalid").should('have.length', 0);
  });

  it("displays the form in preview", () => {
    cy.get(".comment-form form [name='preview']").click();
    cy.url().should("eq", Cypress.config().baseUrl + "/comments/post/");

    // The comment is displayed in preview.
    cy.get(".comment-list .comment-box .comment .header")
      .contains("Fulanita de Tal");
    cy.get(".comment-list .comment-box .comment .body")
      .contains("Your story is inspiring.");
  });

  it("submits the form and displays message", () => {
    cy.get(".comment-form form [name='post']").click();
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/sent/");

    // The comment has been sent, and the page displays that a
    // confirmation has been sent by email and requires an action.
    cy.contains('Comment confirmation requested');
    const msg = (
      'A confirmation message has been sent to your email address. '
      + 'Please, click on the link in the message to confirm your comment.'
    )
    cy.contains(msg);
  });
});
