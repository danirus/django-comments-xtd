describe("Test /12-def-dark--moderated_js", () => {

  beforeEach(() => {
    cy.visit("/12-def-dark--moderated_js");
    // Requires login. Then it redirects to the target URL.
    cy.get("form [name='email']").type("isabel.azul@example.com");
    cy.get("form [name='password']").type("isabel.azul");
    cy.get("form [name='remember']").check();
    cy.get("form [name='submit']").click();
  });

  it("has a form without fields nor buttons", () => {
    cy.get(".comment-form form input").should("have.length", 0);
    cy.get(".comment-form form textarea").should("have.length", 0);
    cy.get(".comment-form form button").should("have.length", 0);
  });

  it("indicates that the comment is in moderation", () => {
    cy.get(".comment-form form div div")
      .should("have.class", "alert", "alert-info", "text-center")
      .should("contain", "Your comment is in moderation.")
      .should("contain", "It needs to be reviewed before publication.")
      .should("contain", "Thank you for your patience and understanding.");
  });
});
