describe('On window.djcx.comment_form', () => {
  beforeEach(() => {
    cy.visit("/def-dark--comment-form");
  });

  it('has not an element with [data-djcx=comment-form]', () => {
    cy.get('[data-djcx=comment-form]').should("not.exist");
  });

  it('does not submit the form when there are missing required fields', () => {
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
      .should("equal", "Please fill out this field.");

    // Field with name='name' is invalid.
    cy.get(".comment-form form [name='name']:invalid")
      .invoke("prop", "validationMessage")
      .should("equal", "Please fill out this field.");

    // Field with name='email' is invalid.
    cy.get(".comment-form form [name='email']:invalid")
      .invoke("prop", "validationMessage")
      .should("equal", "Please fill out this field.");
    });
});
