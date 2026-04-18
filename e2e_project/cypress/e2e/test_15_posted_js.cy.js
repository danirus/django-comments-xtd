describe('Test /15-logout-and-def-dark--comment-posted-js', () => {
  beforeEach(() => {
    cy.visit('/15-logout-and-def-dark--comment-posted-js');
  });

  it("has a form without fields nor buttons", () => {
    cy.get(".comment-form form input").should("have.length", 0);
    cy.get(".comment-form form textarea").should("have.length", 0);
    cy.get(".comment-form form button").should("have.length", 0);
  });

  it('displays expected header, alert-info and text', () => {
    cy.get(".comment-form h5")
      .should('have.text', 'Post your comment');

    cy.get(".comment-form > form > div > div")
      .should("have.class", "alert", "alert-info", "text-center")
      .should("contain", "Comment confirmation requested");

    cy.get(".comment-form > form > div > p")
      .should(
        "contain",
        "A confirmation message has been sent to your email address. "
        + "Please, click on the link in the message to confirm your comment."
      );
  });
});
